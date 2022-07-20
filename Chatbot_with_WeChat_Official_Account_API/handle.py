import web
import hashlib
import receive
import reply
import requests
import json

botIp = "172.31.2.62" # rasabot IP
botPort = '5002'

def get_chat_content(userid,content):
    params = {"sender":userid,"message":content}
    rasaUrl = "http://{0}:{1}/webhooks/rest/webhook".format(botIp, botPort)
    response = requests.post(
        rasaUrl, 
        data = json.dumps(params),
        headers = {'Content-Type':'application/json'}
    )
    return response.text.encode('utf-8').decode("unicode-escape")

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
            webData = web.data()
            print("Handle Post webdata is ", webData.decode('utf-8'))
            recMsg = receive.parse_xml(webData)
            # dealing with text messages
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                # receive messages
                recContent = recMsg.Content.decode('utf-8')
                print("user message:", recContent,type(recContent))
                if recContent == "/stop":
                    exit()
                msgID = recMsg.MsgId
                print("user message ID :", msgID,type(recContent))
                result = get_chat_content(msgID, recContent)
                result_json = json.loads(result)
                # reply messages
                replyContent = ""
                for i in range(len(result_json)):
                    bot_utterence = result_json[i]["text"]
                    print("Bot:",bot_utterence)
                    replyContent += bot_utterence
                print("bot recContent: ", replyContent)
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                replyMsg = reply.TextMsg(toUser, fromUser, replyContent)
                return replyMsg.send()
            else:
                print("暂且不处理")
                return "success"
        except Exception as Argment:
            return Argment