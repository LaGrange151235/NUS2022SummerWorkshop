import hashlib
import web
import receive
import reply

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
            # recMsg is the message client will receive
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
                # decoding message
                recContent = recMsg.Content.decode('utf-8')
                print("user message:", recContent,type(recContent))
                # exchanging sender and receiver
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                # content is the reply message to the user
                content = recContent
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return replyMsg.send()
            else:
                print("暂且不处理")
                return "success"
        except Exception as Argment:
            return Argment
