## 注册微信公众号
首先进入[注册页面](https://mp.weixin.qq.com/cgi-bin/registermidpage?action=index&lang=zh_CN&token=)
![](https://cdn.jsdelivr.net/gh/LaGrange151235/myImage@main/202207182050728.png)
由于我们是个人用户，所以选择订阅号
![](https://cdn.jsdelivr.net/gh/LaGrange151235/myImage@main/202207182053932.png)
然后按照流程注册即可。
## 开启微信公众号开发者模式
在左侧工具栏中选中“设置与开发-基本配置”
![](https://cdn.jsdelivr.net/gh/LaGrange151235/myImage@main/202207182056307.png)
在右侧控制面板中找到“服务器配置”（我的已经启用了），点击“修改配置”
![](https://cdn.jsdelivr.net/gh/LaGrange151235/myImage@main/202207182058219.png)
看到如下内容，其中：
- URL：服务器的ip
- Token：使用者自行设定，之后需要在服务器上自行编码完成验证
- EncodingAESKey：点击“随机生成”即可自动生成
![](https://cdn.jsdelivr.net/gh/LaGrange151235/myImage@main/202207182100224.png)

注意，此时是无法成功提交的，需要在服务器上进行环境配置
## 在服务器上配置Python环境以完成Token验证
以AWS的EC2 instance为例，首先需要安装python和web.py网络框架，可能还需要安装libxml2，libxslt，lxml python等包（以上为[微信推荐的搭建服务框架](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Getting_Started_Guide.html)）
此后需要两个Python脚本来支持Token的验证，首先是main.py作为访问的入口：
<center>main.py</center>

```python
import web
from handle import Handle

urls = (
    '/wx', 'Handle',
)

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
```
然后是handle.py作为Token验证的模块：
<center>handle.py</center>

```python
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
            token = "在这里填写设置的Token"
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
```
然后启动main.py来实现Token验证，注意为了能够访问80端口，可能需要在root模式下执行
```shell
su root
python3 main.py 80
```
正常运行的话应该会在shell看到如下内容：
![](https://cdn.jsdelivr.net/gh/LaGrange151235/myImage@main/202207182115381.png)
同时如果访问http://ip/wx会看到如下内容：
![](https://cdn.jsdelivr.net/gh/LaGrange151235/myImage@main/202207182117330.png)
此时如果在微信公众号平台中验证服务器，则可以通过Token验证，启用开发者模式，在对应服务器上调用微信公众号的API
## 调用微信公众号消息收发API实现复读机机器人
这部分需要修改handle.py来实现，可喜可贺的是微信公众号消息收发API已经被前人封装成了更适合Python脚本调用的形式了，这部分的完整代码一共是四个脚本，这几份脚本可以在[这里](https://github.com/LaGrange151235/NUS2022SummerWorkshop/tree/main/Chatbot_with_WeChat_Official_Account_API)找到
- [main.py](https://github.com/LaGrange151235/NUS2022SummerWorkshop/blob/main/Chatbot_with_WeChat_Official_Account_API/main.py)
- [handle.py](https://github.com/LaGrange151235/NUS2022SummerWorkshop/blob/main/Chatbot_with_WeChat_Official_Account_API/handle.py)
- [receive.py](https://github.com/LaGrange151235/NUS2022SummerWorkshop/blob/main/Chatbot_with_WeChat_Official_Account_API/receive.py)
- [reply.py](https://github.com/LaGrange151235/NUS2022SummerWorkshop/blob/main/Chatbot_with_WeChat_Official_Account_API/reply.py)
## 在关闭shell的情况下保持机器人运行
```shell
nohup python3 main.py 80
```