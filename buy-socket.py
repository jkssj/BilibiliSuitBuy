# -*- coding:utf-8 -*-

# https://github.com/lllk140

from urllib.parse import urlencode
from urllib.parse import urlsplit
from urllib.parse import unquote
from typing import Union
import hashlib
import socket
import uuid
import time
import ssl


class BiliHeader(object):
    def __init__(self, fiddler_raw, **kwargs):
        """
        ? 再等等, 不急
        :param fiddler_raw:
        :param kwargs:
            host: host...
            add_month: 购买时长
            buy_num: 购买数量
            coupon: 优惠卷
            sale_time: 开售时间
            f_source: 来自
            f_from: 来自
        """
        with open(fiddler_raw, "rb") as raw:
            fiddler_content = raw.read()
        raw.close()

        message_dict = self.ParseHttpMessage(fiddler_content)
        cookie_dict = self.cookie_text_to_dict(message_dict["cookie"])

        message_dict.update(kwargs)
        message_dict.update({"cookie_dict": cookie_dict})

        form_data = self.AddFormDataSign(urlencode({
            "access_key": message_dict["access_key"],
            "add_month": kwargs.get("add_month", "-1"),
            "appkey": message_dict["appkey"],
            "buy_num": kwargs.get("buy_num", "1"),
            "coupon_token": kwargs.get("coupon", ""),
            "csrf": cookie_dict["bili_jct"],
            "currency": "bp",
            "disable_rcmd": "0",
            "f_source": kwargs.get("f_source", "shop"),
            "from": kwargs.get("f_from", "feed.card"),
            "from_id": "",
            "item_id": message_dict["item_id"],
            "platform": "android",
            "statistics": message_dict["statistics"],
            "ts": kwargs.get("sale_time", round(time.time())),
        }))

        self.message = self.http_message(form_data, **message_dict)
        self.host = kwargs.get("host", "api.bilibili.com")

    def http_message(self, form_data, **kwargs):
        host = kwargs.get("host", "api.bilibili.com")
        cookie_str = kwargs.get("cookie")
        item_id = kwargs.get("item_id")
        user_agent = kwargs.get("user-agent")

        aurora_eid = kwargs.get("x-bili-aurora-eid")
        cookie_dict = kwargs.get("cookie_dict")

        __f_source = kwargs.get("f_source", "shop")
        __from = kwargs.get("f_from", "feed.card")

        __referer = f"?id={item_id}&navhide=1&f_source={__f_source}&from={__from}"
        __trace_id = self._TraceId(kwargs.get("sale_time", None))

        message = f"POST https://{host}/x/garb/v2/trade/create HTTP/1.1\r\n"
        message += f"native_api_from: h5\r\nCookie: {cookie_str}\r\n"
        message += f"Accept: application/json, text/plain, */*\r\n"
        message += f"Referer: https://www.bilibili.com/h5/mall/suit/detail{__referer}\r\n"
        message += f"env: prod\r\nAPP-KEY: android\r\nUser-Agent: {user_agent}\r\n"
        message += f"x-bili-trace-id: {__trace_id}\r\nx-bili-aurora-eid: {aurora_eid}\r\n"
        message += f"x-bili-mid: {cookie_dict['DedeUserID']}\r\nx-bili-aurora-zone: \r\n"
        message += f"Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n"
        message += f"Content-Length: {len(form_data)}\r\nHost: {host}\r\n"
        message += f"Connection: Keep-Alive\r\nAccept-Encoding: gzip\r\n\r\n{form_data}"
        return message.encode()

    @staticmethod
    def _TraceId(_time: Union[int, float, str] = None):
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
    def cookie_text_to_dict(cookie_text: str):
        cookie_split = cookie_text.split("; ")
        cookie_list = [tuple(i.split("=")) for i in cookie_split]
        return {key: value for key, value in cookie_list}

    @staticmethod
    def ParseHttpMessage(content: bytes):
        body_array, value_dict = content.split(b"\r\n"), dict()
        body_split = [tuple(i.split(b": ")) for i in body_array[1:]]
        body_dict = dict()
        for body_key in body_split:
            key = body_key[0].decode().lower()
            value = list(body_key)[1:]
            value = b"".join(value).decode()
            body_dict[key] = value

        # url—path
        message_url = body_array[0].split(b" ")[1]
        urlsplit_text = urlsplit(message_url.decode("utf-8"))
        verify_path = urlsplit_text.path == "/x/garb/v2/mall/suit/detail"
        assert verify_path, "/x/garb/v2/mall/suit/detail not in HttpMessage"
        url_params = urlsplit_text.query
        params_split = [i.split("=") for i in url_params.split("&")]
        params_dict = {key: value for key, value in params_split}

        access_key = params_dict.get("access_key", None)
        assert access_key, "access_key not in HttpMessage"
        value_dict.update({"access_key": access_key})

        app_key = params_dict.get("appkey", None)
        assert app_key, "appkey not in HttpMessage"
        value_dict.update({"appkey": app_key})

        item_id = params_dict.get("item_id", None)
        assert item_id, "item_id not in HttpMessage"
        value_dict.update({"item_id": item_id})

        statistics = params_dict.get("statistics", None)
        assert statistics, "statistics not in HttpMessage"
        value_dict.update({"statistics": unquote(statistics)})

        # cookie
        cookie_message = body_dict.get("cookie", None)
        assert cookie_message, "cookie not in HttpMessage"
        value_dict.update({"cookie": cookie_message})

        # User-Agent
        user_agent = body_dict.get("user-agent", None)
        assert user_agent, "User-Agent not in HttpMessage"
        value_dict.update({"user-agent": user_agent})

        # x-bili-aurora-eid
        aurora_eid = body_dict.get("x-bili-aurora-eid", None)
        assert aurora_eid, "x-bili-aurora-eid not in HttpMessage"
        value_dict.update({"x-bili-aurora-eid": aurora_eid})

        return value_dict

    def test(self):
        client = ssl.wrap_socket(socket.socket())
        client.connect((self.host, 443))
        client.send(self.message)

        response = bytes()
        rec = client.recv(1024)
        while rec:
            response += rec
            rec = client.recv(1024)
        client.close()
        return response


def main():
    bili = BiliHeader(r"./http_message.txt", sale_time="1662855206")
    print(bili.message.decode())

    response = bili.test()
    print(response.decode())


if __name__ == '__main__':
    main()
