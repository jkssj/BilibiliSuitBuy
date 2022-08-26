# -*- coding:utf-8 -*-

# https://github.com/lllk140


from requests.utils import cookiejar_from_dict
from urllib.parse import urlencode
from typing import Union
import requests
import hashlib
import uuid

DefaultContentType = "application/x-www-form-urlencoded; charset=utf-8"
DefaultAccept = "application/json, text/plain, */*"
DefaultAcceptEncoding = "gzip"
DefaultProxies = {"http": None, "https": None}
DefaultTrustEnv = False
DefaultHost = "api.biliapi.net"
DefaultConnection = "keep-alive"
DefaultHeaderAPPKEY = "android"
DefaultEnv = "prod"
DefaultApiFrom = "h5"


class Generate(object):
    @staticmethod
    def _BiliTraceId(_time: Union[int, float]):
        back6 = hex(round(_time / 256))
        front = str(uuid.uuid4()).replace("-", "")
        _1 = front[6:] + back6[2:]
        _2 = front[22:] + back6[2:]
        return f"{_1}:{_2}:0:0"

    @staticmethod
    def _BiliAddFormDataSign(form_data: str):
        app_sec = "560c52ccd288fed045859ed18bffd973"
        form_data_sec = f"{form_data}{app_sec}"
        md5_hashlib = hashlib.md5()
        md5_hashlib.update(form_data_sec.encode())
        sign = md5_hashlib.hexdigest()
        return form_data + f"&sign={sign}"

    @staticmethod
    def _BiliUserAgent(**kwargs):
        system_version: str = kwargs.get("system_version")
        channel: str = kwargs.get("channel")
        sdk_int: str = kwargs.get("sdk_int")
        version: str = kwargs.get("version")
        session: str = kwargs.get("session")
        buv_id: str = kwargs.get("buv_id")
        phone: str = kwargs.get("phone")
        build: str = kwargs.get("build")

        user_agent_list = [
            f"Mozilla/5.0 (Linux; Android {system_version}; {phone} Build/QP1A.190711.020; wv)",
            f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36",
            f"os/android model/{phone} build/{build} osVer/{system_version} sdkInt/{sdk_int}",
            f"network/2 BiliApp/{build} mobi_app/android channel/{channel} Buvid/{buv_id}",
            f"sessionID/{session} innerVer/{build} c_locale/zh_CN s_locale/zh_CN",
            f"disable_rcmd/0 {version} os/android model/{phone} mobi_app/android build/{build}",
            f"channel/{channel} innerVer/{build} osVer/{system_version} network/2"
        ]
        return " ".join(user_agent_list)


class SuitBuySession(requests.Session, Generate):
    suit_buy_url = "https://api.bilibili.com/x/garb/v2/trade/create"
    app_sec = "560c52ccd288fed045859ed18bffd973"  # 计算sign用的

    def __init__(self, **kwargs):
        super(SuitBuySession, self).__init__()

        # 代理设置
        self.trust_env = kwargs.get("trust_env", DefaultTrustEnv)
        self.proxies = kwargs.get("proxies", DefaultProxies)

        # 表单设置
        __shop_from = kwargs.get("shop_from", "feed.card")
        __coupon_token = kwargs.get("coupon_token", "")
        __f_source: str = kwargs.get("f_source", "shop")
        __sale_time: int = int(kwargs.get("sale_time"))
        __add_month = kwargs.get("add_month", "-1")
        __item_id: str = kwargs.get("item_id")
        __buy_num = kwargs.get("buy_num", "1")
        __app_key: str = kwargs.get("app_key")

        # 访问头设置
        __referer = f"https://www.bilibili.com/h5/mall/suit/detail?id={__item_id}"
        __referer = __referer + f"&navhide=1&f_source=shop&from={__shop_from}"
        __HeaderAPPKEY = kwargs.get("header_app_key", DefaultHeaderAPPKEY)
        __Encoding = kwargs.get("accept_encoding", DefaultAcceptEncoding)
        __content_type = kwargs.get("content_type", DefaultContentType)
        __Connection = kwargs.get("connection", DefaultConnection)
        __ApiFrom = kwargs.get("api_from", DefaultApiFrom)
        __TraceId = self._BiliTraceId(int(__sale_time))
        __Accept = kwargs.get("accept", DefaultAccept)
        __UserAgent = self._BiliUserAgent(**kwargs)
        __host = kwargs.get("host", DefaultHost)
        __Env = kwargs.get("env", DefaultEnv)

        # 用户验证
        __access_key: str = kwargs.get("access_key")
        __bili_eid: str = kwargs.get("bili_eid")
        __suit_cookie: dict = kwargs.get("cookie")
        __bili_jct = __suit_cookie["bili_jct"]

        # 杂项
        __version: str = kwargs.get("version")
        __DedeUserID = __suit_cookie['DedeUserID']
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
            "item_id": str(__item_id),
            "platform": "android",
            "statistics": __statistics,
            "ts": str(__sale_time)
        })

        self.from_data_buy = self._BiliAddFormDataSign(__from_data_buy)
        self.cookies = cookiejar_from_dict(__suit_cookie)
        self.headers.update({"Accept": str(__Accept)})
        self.headers.update({"Accept-Encoding": str(__Encoding)})
        self.headers.update({"User-Agent": str(__UserAgent)})
        self.headers.update({"Content-Length": str(len(self.from_data_buy))})
        self.headers.update({"Content-Type": str(__content_type)})
        self.headers.update({"APP-KEY": str(__HeaderAPPKEY)})
        self.headers.update({"env": str(__Env)})
        self.headers.update({"native_api_from": str(__ApiFrom)})
        self.headers.update({"Referer": str(__referer)})
        self.headers.update({"x-bili-aurora-eid": str(__bili_eid)})
        self.headers.update({"x-bili-aurora-zone": ""})
        self.headers.update({"x-bili-mid": str(__DedeUserID)})
        self.headers.update({"x-bili-trace-id": str(__TraceId)})
        self.headers.update({"Connection": str(__Connection)})
        self.headers.update({"Host": str(__host)})


class SuitBuy(SuitBuySession):
    def __init__(self, **kwargs):
        super(SuitBuy, self).__init__(**kwargs)

    def PrintValue(self):
        print(self.headers)
        print(self.cookies)
        print(self.trust_env)
        print(self.proxies)
        print(self.from_data_buy)

    def run(self):
        suit_buy_url = "https://api.bilibili.com/x/garb/v2/trade/create"
        response = self.post(suit_buy_url, data=self.from_data_buy)
        return response


if __name__ == '__main__':
    from test_value import cookie_test, access_key_test, bili_eid_test
    import time
    suit = SuitBuy(
        trust_env=False,
        proxies={"http": None, "https": None},

        # 装扮设置
        shop_from="feed.card",
        coupon_token="",
        f_source="shop",
        add_month="-1",
        item_id="37825",
        buy_num="1",
        sale_time=round(time.time()),
        app_key="1d8b6e7d45233436",

        # 访问头设置(外)
        header_app_key=DefaultHeaderAPPKEY,
        accept_encoding=DefaultAcceptEncoding,
        content_type=DefaultContentType,
        connection=DefaultConnection,
        api_from=DefaultApiFrom,
        accept=DefaultAccept,
        host=DefaultHost,
        env=DefaultEnv,

        # 访问头设置(UserAgent)
        system_version="9",
        channel="yingyongbao",
        sdk_int="28",
        version="6.87.0",
        session="1a7fb931",
        buv_id="XY30A9D303849C51D0D6F863F84A269E887E8",
        phone="M2007J22C",
        build="6870300",

        # 用户验证
        access_key=access_key_test,
        bili_eid=bili_eid_test,
        cookie=cookie_test
    )
    suit.PrintValue()
    print(suit.run())
