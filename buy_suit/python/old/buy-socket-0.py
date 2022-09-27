from urllib.parse import urlencode
import hashlib
import socket
import time
import uuid
import ssl


class SocketClient(object):
    app_sec = "560c52ccd288fed045859ed18bffd973"

    def __init__(self, item_id, host, port=443, **kwargs):
        self.item_id, self.host = item_id, host
        self.client = ssl.wrap_socket(socket.socket())
        self.client.connect((host, port))

        self.cookie_dict: dict = kwargs.get("cookie", None)
        assert self.cookie_dict, "cookie not in kwargs"

        message_body = self.message_body(**kwargs)
        self.message = self.request_message(message_body, **kwargs)

    def __del__(self):
        self.client.close()

    @staticmethod
    def x_bili_trace_id(sale_time):
        back6 = hex(round(sale_time / 256))
        front = str(uuid.uuid4()).replace("-", "")
        _1 = front[6:] + back6[2:]
        _2 = front[22:] + back6[2:]
        return f"{_1}:{_2}:0:0"

    @staticmethod
    def AddFormDataSign(form_data: str):
        app_sec = "560c52ccd288fed045859ed18bffd973"
        form_data_sec = f"{form_data}{app_sec}"
        md5_hashlib = hashlib.md5()
        md5_hashlib.update(form_data_sec.encode())
        sign = md5_hashlib.hexdigest()
        return form_data + f"&sign={sign}"

    def request_message(self, message_body: str, **kwargs):
        cookie_text = "; ".join(["=".join(i) for i in self.cookie_dict.items()])
        __f_source = kwargs.get("f_source", "shop")
        __shop_from = kwargs.get("shop_from", "feed.card")
        __User_Agent = kwargs.get("user_agent", None)
        __sale_time = kwargs.get("sale_time", time.time())
        __aurora_eid = kwargs.get("x_bili_aurora_eid", None)
        referer_params = f"?id={self.item_id}&f_source={__f_source}&from={__shop_from}"

        assert __aurora_eid, "aurora_eid not in kwargs"
        assert __User_Agent, "user_agent not in kwargs"

        message = f"POST https://{self.host}/x/garb/v2/trade/create HTTP/1.1\r\n"
        message += f"native_api_from: h5\r\n"
        message += f"Cookie: {cookie_text}\r\n"
        message += f"Accept: application/json, text/plain, */*\r\n"
        message += f"Referer: https://www.bilibili.com/h5/mall/suit/detail{referer_params}\r\n"
        message += f"env: prod\r\n"
        message += f"APP-KEY: android\r\n"
        message += f"User-Agent: {__User_Agent}\r\n"
        message += f"x-bili-trace-id: {self.x_bili_trace_id(__sale_time)}\r\n"
        message += f"x-bili-aurora-eid: {__aurora_eid}\r\n"
        message += f"x-bili-mid: {self.cookie_dict['DedeUserID']}\r\n"
        message += f"x-bili-aurora-zone: \r\n"
        message += f"Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n"
        message += f"Content-Length: {len(message_body)}\r\n"
        message += f"Host: {self.host}\r\n"
        message += f"Connection: Keep-Alive\r\n"
        message += f"Accept-Encoding: gzip\r\n\r\n"
        message += f"{message_body}"
        return message

    def message_body(self, **kwargs):
        __access_key: str = kwargs.get("access_key")
        __bili_jct = self.cookie_dict["bili_jct"]
        __add_month = kwargs.get("add_month", "-1")
        __buy_num = kwargs.get("buy_num", "1")
        __app_key: str = kwargs.get("app_key")
        __shop_from = kwargs.get("shop_from", "feed.card")
        __coupon_token = kwargs.get("coupon_token", "")
        __f_source: str = kwargs.get("f_source", "shop")
        __version: str = kwargs.get("version")
        __sale_time = kwargs.get("sale_time", time.time())

        __statistics = '{"appId":1,"platform":3,"version":"__version__","abtest":""}'
        __statistics = __statistics.replace("__version__", __version)

        __from_data_buy = urlencode({
            "access_key": __access_key,
            "add_month": str(__add_month),
            "appkey": str(__app_key),
            "buy_num": str(__buy_num),
            "coupon_token": str(__coupon_token),
            "csrf": str(__bili_jct),
            "currency": "bp",
            "disable_rcmd": "0",
            "f_source": str(__f_source),
            "from": str(__shop_from),
            "from_id": "",
            "item_id": str(self.item_id),
            "platform": "android",
            "statistics": __statistics,
            "ts": str(__sale_time)
        })
        message_body = self.AddFormDataSign(__from_data_buy)
        return message_body

    def send(self):
        self.client.sendall(self.message.encode())

    def recv(self):
        response = bytes()
        rec = self.client.recv(1024)
        while rec:
            response += rec
            rec = self.client.recv(1024)
        self.client.close()
        return response


if __name__ == '__main__':
    from config import a_config
    # test
    suit = SocketClient(
        "3717", "api.biliapi.net", 443,

        # 装扮设置
        shop_from="search.list",
        coupon_token="",
        f_source="shop",
        add_month="-1",
        buy_num="1",
        sale_time=1662395559,
        app_key="1d8b6e7d45233436",
        version="6.88.0",

        user_agent="Mozilla/5.0 (Linux; Android 9; SM-G9810 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36 os/android model/SM-G9810 build/6880300 osVer/9 sdkInt/28 network/2 BiliApp/6880300 mobi_app/android channel/yingyongbao Buvid/XY30A9D303849C51D0D6F863F84A269E887E8 sessionID/d28f20e5 innerVer/6880300 c_locale/zh_CN s_locale/zh_CN disable_rcmd/0 6.88.0 os/android model/SM-G9810 mobi_app/android build/6880300 channel/yingyongbao innerVer/6880300 osVer/9 network/2",
        # 用户验证
        access_key=a_config["access_key"],
        x_bili_aurora_eid=a_config["bili_eid"],
        cookie=a_config["cookies"]
    )
    print(suit.message)
    suit.send()
    print(suit.recv().decode())
