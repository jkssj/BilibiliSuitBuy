# -*- coding:utf-8 -*-

# https://github.com/lllk140
# https://python-hyper.org/projects/h2/en/stable/plain-sockets-example.html

from urllib.parse import urlencode
from urllib.parse import urlsplit
from urllib.parse import unquote
import h2.connection
import h2.events
import hashlib
import socket
import uuid
import time
import ssl
import h2


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
        headers = {unquote(i[0]).lower(): i[1] for i in h3}

        cookies_content: str = headers.get("cookie")
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

        self.h2connection = self.BuildH2(sale_time, headers, form_data)

        # h2报文
        __message = self.h2connection.data_to_send()
        self.message_header = __message[:-1]
        self.message_body = __message[-1:]

    def BuildH2(self, sale_time: int, headers: dict, form_data: str):
        h2connection = h2.connection.H2Connection()
        h2connection.initiate_connection()

        __headers = [
            (":method", "POST"),
            (":path", "/x/garb/v2/trade/create"),
            (":authority", self.host),
            (":scheme", "https"),
            ("native_api_from", headers["native_api_from"]),
            ("accept", headers["accept"]),
            ("referer", headers["referer"]),
            ("env", headers["env"]),
            ("app-key", headers["app-key"]),
            ("user-agent", headers["user-agent"]),
            ("x-bili-trace-id", self.BiliTraceId(sale_time)),
            ("x-bili-aurora-eid", headers["x-bili-aurora-eid"]),
            ("x-bili-mid", headers["x-bili-mid"]),
            ("x-bili-aurora-zone", headers["x-bili-aurora-zone"]),
            ("content-type", "application/x-www-form-urlencoded; charset=utf-8"),
            ("content-length", str(len(form_data))),
            ("accept-encoding", headers["accept-encoding"]),
            ("cookie", headers["cookie"]),
        ]

        h2connection.send_headers(1, __headers)
        h2connection.send_data(1, form_data.encode(), end_stream=True)

        return h2connection


class SuitBuy(SuitValue):
    def __init__(self, http_message: bytes, sale_time: int, **kwargs):
        super(SuitBuy, self).__init__(http_message, sale_time, **kwargs)

    def CreateTlsConnection(self, port: int = 443, **kwargs) -> ssl.SSLSocket:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.set_alpn_protocols(["h2"])
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

    def ReceiveResponse(self, client: ssl.SSLSocket, length=4096) -> bytes:
        """ 接收响应 """
        response = bytes()
        recv_data = client.recv(length)
        while recv_data:
            events = self.h2connection.receive_data(recv_data)
            for event in events:
                if isinstance(event, h2.events.DataReceived):
                    args = (event.flow_controlled_length, event.stream_id)
                    self.h2connection.acknowledge_received_data(*args)
                    response += event.data
                if isinstance(event, h2.events.StreamEnded):
                    client.sendall(self.h2connection.data_to_send())
                    return response

            client.sendall(self.h2connection.data_to_send())
            recv_data = client.recv(length)

        return response

    def ClientClose(self, client: ssl.SSLSocket) -> None:
        self.h2connection.close_connection()
        client.sendall(self.h2connection.data_to_send())
        client.close()

    def demo(self, port=443, **kwargs):
        client = self.CreateTlsConnection(port, **kwargs)

        s = time.time()

        self.SendMessageHeader(client)
        self.SendMessageBody(client)

        response = self.ReceiveResponse(client)

        e = time.time()

        self.ClientClose(client)

        return response.decode(errors="ignore"), e - s


def main():
    sale_time = 1665901776

    suit_buy = SuitBuy(
        http_message=open(r"../http-message/HTTP2.0Message.txt", "rb").read(),
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
    # suit_buy.ClientClose(client)


if __name__ == '__main__':
    main()
