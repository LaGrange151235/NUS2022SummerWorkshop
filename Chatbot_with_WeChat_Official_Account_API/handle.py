import web
import hashlib
import receive
import reply
import requests
import json
import pymysql
import time
import db_fuc as dbf

# ---rasa bot data--- #
botIp = (
        "172.31.2.62",  # rasabot1 IP
        "172.31.8.76"   # rasabot2 IP
        )
botPort = '5002'
rasa_bot_n = 2
# ---rasa bot data--- #

# get_chat_content: sent message to rasa bot server and get reply
# - userid: who sent this message to chatbot
# - content: message content
# - botIp: the private IP of rasa bot server
def get_chat_content(userid,content,botIp):
    params = {"sender":userid,"message":content}
    rasaUrl = "http://{0}:{1}/webhooks/rest/webhook".format(botIp, botPort)
    response = requests.post(
        rasaUrl, 
        data = json.dumps(params),
        headers = {'Content-Type':'application/json'}
    )
    return response.text.encode('utf-8').decode("unicode-escape")

# receive_message: get message sent by any users
def receive_message():
    webData = web.data()
    #print("Handle Post webdata is ", webData.decode('utf-8'))
    recMsg = receive.parse_xml(webData)
    return recMsg

# reply_message: send back reply message
# - recMsg: the message chatbot received
# - botIp: the private IP of rasa bot server
def reply_message(recMsg, botIp):
    # receive messages
    recContent = recMsg.Content.decode('utf-8')
    if recContent == "/stop":
        exit()
    userID = recMsg.FromUserName
    print("user ID :", userID,type(recContent))
    print("user message:", recContent,type(recContent))
                
    # reply messages
    result = get_chat_content(userID, recContent, botIp)
    result_json = json.loads(result)
    replyContent = ""
    for i in range(len(result_json)):
        bot_utterence = result_json[i]["text"]
        #print("Bot:",bot_utterence)
        replyContent += bot_utterence
    print("bot recContent: ", replyContent)
    toUser = recMsg.FromUserName
    fromUser = recMsg.ToUserName
    replyMsg = reply.TextMsg(toUser, fromUser, replyContent)
    return replyMsg.send()

class Handle(object):
    def GET(self):
        try:
            data = web.input()
            print(data)
            if len(data) == 0:
                return "hello, this is handle view"
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = "111"
            li = [token, timestamp, nonce]
            li.sort()
            tmp_str = "".join(li).encode('utf-8')
            #sha1 encipher
            hashcode = hashlib.sha1(tmp_str).hexdigest()
            print("handle/GET func: hashcode, signature: ", hashcode, signature)
            if hashcode == signature:
                return echostr
            else:
                return ""
        except Exception as Argument:
            return Argument
    def POST(self):
        try:
            print("\n--------------------")
            recMsg = receive_message()
            # dealing with text messages
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                
                #---paras---#
                userID = recMsg.FromUserName
                text_time = time.time()
                db = dbf.connect_to_database()
                cursor = db.cursor()
                last_time = dbf.search_table_USERS(cursor, "LAST_TEXT", "NAME", userID)
                #---paras---#

                #---reply---#
                # 1. New Users: 
                #   1.1. get rasa server ip
                #   1.2. insert into USERS table in database
                #   1.3. send back reply
                if not last_time:
                    server = dbf.find_suitable_SERVERS(cursor, rasa_bot_n+1)
                    dbf.insert_into_USERS(db, cursor, userID, text_time, server)
                    result = reply_message(recMsg, botIp[server-1])
                # 2. Users in record: 
                #   2.1. get previous rasa server ip
                #   2.2. update last_text time info in database
                #   2.3. send back reply
                else:
                    server = dbf.search_table_USERS(cursor, "RASA_SERVER", "NAME", userID)[0][0]
                    dbf.update_set_USERS(db, cursor, userID, text_time)
                    result = reply_message(recMsg, botIp[int(server)-1])
                #---reply---#

                #---update database---#
                # if any user doesn't send message 
                # to chatbot for more than 1 min(60 s)
                # remove it from the USERS table
                time_bond = text_time - 60
                dbf.delete_early_USERS(db, cursor, time_bond)
                #---update database---#
                return result
            else:
                print("暂且不处理")
                return "success"
        except Exception as Argment:
            return Argment