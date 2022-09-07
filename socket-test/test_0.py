# socket-test

import socket
import time
import ssl


class SocketClient(object):
    def __init__(self, host, port):
        self.host = host
        self.client = ssl.wrap_socket(socket.socket())
        self.client.connect((host, port))

    def message(self):
        _a = "navhide=1&from=search.list&id=3717&f_source=shop&native.theme=1"
        request_message = f"GET https://{self.host}/x/garb/order/item/count/unpaid?item_id=3717 HTTP/1.1\r\n"
        request_message += f"native_api_from: h5\r\n"
        request_message += f"Accept: application/json, text/plain, */*\r\n"
        request_message += f"Referer: https://www.bilibili.com/h5/mall/suit/detail?{_a}\r\n"
        request_message += f"Content-Type: application/json\r\n"
        request_message += f"env: prod\r\n"
        request_message += f"APP-KEY: android\r\n"
        request_message += f"User-Agent: Mozilla/5.0 (Linux; Android 9; SM-G9810 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 os/android model/SM-G9810 build/6880300 osVer/9 sdkInt/28 network/2 BiliApp/6880300 mobi_app/android channel/yingyongbao Buvid/XY30A9D303849C51D0D6F863F84A269E887E8 sessionID/d28f20e5 innerVer/6880300 c_locale/zh_CN s_locale/zh_CN disable_rcmd/0 6.88.0 os/android model/SM-G9810 mobi_app/android build/6880300 channel/yingyongbao innerVer/6880300 osVer/9 network/2\r\n"
        request_message += f"Host: {self.host}\r\n"
        request_message += f"Connection: Keep-Alive\n"
        request_message += f"Accept-Encoding: gzip\r\n\r\n"
        return request_message

    def send(self, message: str):
        print(time.time_ns())
        self.client.sendall(message.encode())
        print(time.time_ns())

    def recv(self):
        print(time.time_ns())
        response = bytes()
        rec = self.client.recv(1024)
        while rec:
            response += rec
            rec = self.client.recv(1024)
        self.client.close()
        return response


if __name__ == '__main__':
    client = SocketClient("api.biliapi.net", 443)
    client.send(client.message())
    print(client.recv())
