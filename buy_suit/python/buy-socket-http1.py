# -*- coding:utf-8 -*-

# https://github.com/lllk140

from urllib.parse import urlencode
from urllib.parse import urlsplit
from urllib.parse import unquote
import hashlib
import socket
import uuid
import time
import ssl


class Tools(object):
    def __init__(self):
        super(Tools, self).__init__()

    @staticmethod
    def BiliTraceId(_time: int | float | str = None):
        _time = float(_time) if _time else time.time()
        back6 = hex(round(_time / 256))
        front = str(uuid.uuid4()).replace("-", "")
        _data1 = front[6:] + back6[2:]
        _data2 = front[22:] + back6[2:]
        return f"{_data1}:{_data2}:0:0"

    @staticmethod
    def AddFormDataSign(form_data: str):
        app_sec = "560c52ccd288fed045859ed18bffd973"
        form_data_sec = f"{form_data}{app_sec}"
        md5_hashlib = hashlib.md5()
        md5_hashlib.update(form_data_sec.encode())
        sign = md5_hashlib.hexdigest()
        return form_data + f"&sign={sign}"

    @staticmethod
    def BuildFormData(sale_time, **kwargs):
        __add_month = kwargs.get("add_month", "-1")
        __buy_num = kwargs.get("buy_num", "1")
        __coupon_token = kwargs.get("coupon_token", "")
        __f_source = kwargs.get("f_source", "shop")
        __shop_from = kwargs.get("shop_from", "feed.card")

        __statistics = kwargs["statistics"]
        __access_key = kwargs["access_key"]
        __item_id = kwargs["item_id"]
        __app_key = kwargs["appkey"]
        __csrf = kwargs["csrf"]

        form_data_text = urlencode({
            "access_key": __access_key,
            "add_month": str(__add_month),
            "appkey": str(__app_key),
            "buy_num": str(__buy_num),
            "coupon_token": str(__coupon_token),
            "csrf": str(__csrf),
            "currency": "bp",
            "disable_rcmd": "0",
            "f_source": str(__f_source),
            "from": str(__shop_from),
            "from_id": "",
            "item_id": str(__item_id),
            "m_source": "",
            "platform": "android",
            "statistics": __statistics,
            "ts": str(sale_time)
        })
        return form_data_text

    @staticmethod
    def ParseHttpMessage(content: bytes) -> tuple[dict, dict, dict]:
        message_content: list = content.split(b"\r\n")

        request: list = message_content[0].split(b" ")
        url_query: bytes = urlsplit(request[1]).query
        p = [i.split(b"=") for i in url_query.split(b"&")]
        p2 = [[ii.decode() for ii in i] for i in p]
        params = {unquote(i[0]): unquote(i[1]) for i in p2}

        headers_content = message_content[1:len(message_content) - 2]
        h = [i.split(b": ") for i in headers_content]
        h2 = [i if len(i) == 2 else [i[0], b""] for i in h]
        h3 = [[ii.decode() for ii in i] for i in h2]
        headers = {unquote(i[0]): i[1] for i in h3}

        __key = "Cookie" if "Cookie" in headers else "cookie"
        cookies_content: str = headers.get(__key)
        c1: list = cookies_content.split("; ")
        c2 = [i.split("=") for i in c1]
        cookies = {i[0]: i[1] for i in c2}

        return params, headers, cookies


class SuitValue(Tools):
    def __init__(self, http_message: bytes, sale_time: int, **kwargs):
        super(Tools, self).__init__()

        self.host = kwargs.get("host", "api.bilibili.com")

        params, headers, cookies = self.ParseHttpMessage(http_message)

        kwargs.update({"csrf": params["csrf"]})
        kwargs.update({"appkey": params["appkey"]})
        kwargs.update({"item_id": params["item_id"]})
        kwargs.update({"access_key": params["access_key"]})
        kwargs.update({"statistics": params["statistics"]})

        # 表单
        form_data_content = self.BuildFormData(sale_time, **kwargs)
        form_data: str = self.AddFormDataSign(form_data_content)

        # 完整报文
        __message = self.BuildMessage(sale_time, headers, form_data)
        self.message_header = __message[:-1]
        self.message_body = __message[-1:]

    def BuildMessage(self, sale_time: int, headers: dict, form_data: str):
        message = "POST /x/garb/v2/trade/create HTTP/1.1\r\n"
        message += f"native_api_from: {headers['native_api_from']}\r\n"
        message += f"Cookie: {headers['Cookie']}\r\n"
        message += f"Accept: {headers['Accept']}\r\n"
        message += f"Referer: {headers['Referer']}\r\n"
        message += f"env: {headers['env']}\r\n"
        message += f"APP-KEY: {headers['APP-KEY']}\r\n"
        message += f"User-Agent: {headers['User-Agent']}\r\n"
        message += f"x-bili-trace-id: {self.BiliTraceId(sale_time)}\r\n"
        message += f"x-bili-aurora-eid: {headers['x-bili-aurora-eid']}\r\n"
        message += f"x-bili-mid: {headers['x-bili-mid']}\r\n"
        message += f"x-bili-aurora-zone: {headers['x-bili-aurora-zone:']}\r\n"
        message += f"Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n"
        message += f"Content-Length: {str(len(form_data))}\r\n"
        message += f"Host: {self.host}\r\n"
        message += f"Connection: {headers['Connection']}\r\n"
        message += f"Accept-Encoding: {headers['Accept-Encoding']}\r\n\r\n"
        return str(message + form_data).encode()


class SuitBuy(SuitValue):
    def __init__(self, http_message: bytes, sale_time: int, **kwargs):
        super(SuitBuy, self).__init__(http_message, sale_time, **kwargs)

    def CreateTlsConnection(self, port: int = 443, **kwargs) -> ssl.SSLSocket:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.purpose = ssl.Purpose.SERVER_AUTH
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_default_certs()
        _connection = socket.create_connection((self.host, port))
        kwargs.update({"server_hostname": self.host})
        connection = context.wrap_socket(_connection, **kwargs)
        return connection

    def SendMessageHeader(self, client: ssl.SSLSocket):
        return client.send(self.message_header)

    def SendMessageBody(self, client: ssl.SSLSocket):
        return client.send(self.message_body)

    @staticmethod
    def ReceiveResponse(client: ssl.SSLSocket, length=4096) -> bytes:
        return client.recv(length)

    def demo(self, port=443, **kwargs):
        # 创建连接
        client = self.CreateTlsConnection(port, **kwargs)

        s = time.time()

        # 发送报文
        self.SendMessageHeader(client)
        self.SendMessageBody(client)

        # 接收响应
        response = self.ReceiveResponse(client)

        e = time.time()

        print(response.decode())
        print(e - s)
        client.close()
        return response, e - s


def main():
    sale_time = 1665889008

    suit_buy = SuitBuy(
        http_message=open(r"../http-message/HTTP1.1Message.txt", "rb").read(),
        sale_time=sale_time,

        # 可选
        add_month="-1",
        buy_num="1",
        coupon_token="",
        host="api.bilibili.com",
        f_source="shop",
        shop_from="feed.card",
    )

    # 演示
    response, run_time = suit_buy.demo()
    print(response, run_time)

    # 跳出本地计时器后
    # client = suit_buy.CreateTlsConnection()
    # suit_buy.SendMessageHeader(client)

    # 等待服务器计时退出
    # suit_buy.SendMessageBody(client)
    # response = suit_buy.ReceiveResponse(client)

    # print(response.decode())
    
    # 关闭连接
    # client.close()


if __name__ == '__main__':
    main()
