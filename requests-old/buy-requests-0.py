# -*- coding:utf-8 -*-

# https://github.com/lllk140

from requests.utils import cookiejar_from_dict
from urllib.parse import urlencode
import requests
import hashlib
import uuid


class SuitBuySession(requests.Session):
    suit_buy_url = "https://api.bilibili.com/x/garb/v2/trade/create"
    app_sec = "560c52ccd288fed045859ed18bffd973"  # 计算sign用的
    DefaultProxies = {"http": None, "https": None}
    DefaultTrustEnv = False

    def __init__(self, **kwargs):
        super(SuitBuySession, self).__init__()
        self.system_version: str = kwargs.get("system_version")
        self.access_key: str = kwargs.get("access_key")
        self.app_key: str = kwargs.get("app_key")
        self.channel: str = kwargs.get("channel")
        self.version: str = kwargs.get("version")
        self.sdk_int: str = kwargs.get("sdk_int")
        self.item_id: str = kwargs.get("item_id")
        self.buv_id: str = kwargs.get("buv_id")
        self.phone: str = kwargs.get("phone")
        self.build: str = kwargs.get("build")

        self.add_month = kwargs.get("add_month", "-1")
        self.buy_num = kwargs.get("buy_num", "1")
        self.coupon_token = kwargs.get("coupon_token", "")
        self.sale_time = kwargs.get("sale_time")

        __referer = f"https://www.bilibili.com/h5/mall/suit/detail?id={self.item_id}"
        __referer += "&navhide=1&f_source=shop&from=feed.card"
        __content_type = "application/x-www-form-urlencoded; charset=utf-8"
        __suit_cookie = kwargs.get("cookie")

        self.__bili_jct = __suit_cookie["bili_jct"]
        self.suit_buy_data, data_len = self.__data()

        self.cookies = cookiejar_from_dict(__suit_cookie)
        self.trust_env = kwargs.get("trust_env", self.DefaultTrustEnv)
        self.proxies = kwargs.get("trust_env", self.DefaultProxies)
        self.headers.update({"Accept": "application/json, text/plain, */*"})
        self.headers.update({"Accept-Encoding": "gzip"})
        self.headers.update({"User-Agent": self.__UserAgent()})
        self.headers.update({"Content-Length": str(data_len)})
        self.headers.update({"Content-Type": __content_type})
        self.headers.update({"APP-KEY": "android"})
        self.headers.update({"env": "prod"})
        self.headers.update({"native_api_from": "h5"})
        self.headers.update({"Referer": __referer})
        self.headers.update({"x-bili-aurora-eid": ""})
        self.headers.update({"x-bili-aurora-zone": ""})
        self.headers.update({"x-bili-mid": f"{__suit_cookie['DedeUserID']}"})
        self.headers.update({"x-bili-trace-id": self.__TraceId()})
        self.headers.update({"Connection": "keep-alive"})
        self.headers.update({"Host": "api.biliapi.net"})

    def __UserAgent(self):
        user_agent_list = [
            f"Mozilla/5.0 (Linux; Android {self.system_version}; {self.phone} Build/QP1A.190711.020; wv)",
            f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36",
            f"os/android model/{self.phone} build/{self.build} osVer/{self.system_version} sdkInt/{self.sdk_int}",
            f"network/2 BiliApp/{self.build} mobi_app/android channel/{self.channel} Buvid/{self.buv_id}",
            f"innerVer/{self.build} c_locale/zh_CN s_locale/zh_CN disable_rcmd/0 {self.version} os/android",
            f"model/{self.phone} mobi_app/android build/{self.build} channel/{self.channel} innerVer/{self.build}",
            f"osVer/{self.system_version} network/2"
        ]
        return " ".join(user_agent_list)

    def __TraceId(self):
        a, b = "".join(str(uuid.uuid4()).split("-")), hex(int(self.item_id))
        return a[0:26] + b[2:8] + ":" + a[16:26] + b[2:8] + ":0:0"

    def __data(self):
        statistics_ = '{"appId":1,"platform":3,"version":"__version__","abtest":""}'
        statistics = statistics_.replace("__version__", self.version)
        data_str = urlencode({
            "access_key": self.access_key,
            "add_month": str(self.add_month),
            "appkey": str(self.app_key),
            "buy_num": str(self.buy_num),
            "coupon_token": str(self.coupon_token),
            "csrf": self.__bili_jct,
            "currency": "bp",
            "disable_rcmd": "0",
            "f_source": "shop",
            "from": "feed.card",
            "from_id": "",
            "item_id": str(self.item_id),
            "platform": "android",
            "statistics": statistics,
            "ts": str(self.sale_time)
        })
        md5_data = f"{data_str}{self.app_sec}"
        md5_hashlib = hashlib.md5()
        md5_hashlib.update(md5_data.encode())
        sign = md5_hashlib.hexdigest()
        all_data = data_str + f"&sign={sign}"
        return all_data, len(all_data)


class SuitBuy(SuitBuySession):
    def __init__(self, **kwargs):
        super(SuitBuy, self).__init__(**kwargs)

    def start(self):
        response = self.post(self.suit_buy_url, data=self.suit_buy_data)
        print(response.text)


if __name__ == '__main__':
    from test_value import cookie_test, access_key_test, buv_id_test
    suit = SuitBuy(
        cookie=cookie_test,
        buv_id=buv_id_test,
        access_key=access_key_test,
        app_key="1d8b6e7d45233436",
        item_id="37644",
        phone="M2007J22C",
        channel="yingyongbao",
        system_version="9",
        sdk_int="28",
        version="6.87.0",
        build="6870300",

        sale_time="1661322078"
    )
    print(suit.headers)
    print(suit.suit_buy_data)
    print(suit.cookies)
    print(suit.trust_env)
    print(suit.proxies)
    # suit.start()
