from requests.utils import cookiejar_from_dict
from urllib.parse import urlencode
from typing import Union
import requests
import hashlib
import uuid
import time


class BiliSession(requests.Session):
    def __init__(self, **kwargs):
        super(BiliSession, self).__init__()

        # 代理
        self.trust_env = kwargs.get("trust_env", False)
        self.proxies = kwargs.get("proxies", None)

        # cookie
        __cookies: dict = kwargs.get("cookies", None)
        assert __cookies, "cookies not in kwargs"
        self.cookies = cookiejar_from_dict(__cookies)

        # cookie to other
        self.BiliCsrf = __cookies["bili_jct"]
        self.UserId = __cookies["DedeUserID"]

        # other
        __version: str = kwargs.get("version")
        assert __version, "version not in kwargs"
        self.statistics = str(self._BiliStatistics(__version))

        # x-bili-aurora-eid
        __BiliEid = kwargs.get("bili_eid", None)
        assert __cookies, "bili_eid not in kwargs"

        # Host and url
        __Host = kwargs.get("host", "api.biliapi.net")
        self.unpaid_url = ("GET", f"https://{__Host}/x/garb/order/item/count/unpaid")
        self.detail_url = ("GET", f"https://{__Host}/x/garb/v2/mall/suit/detail")
        self.nav_url = ("GET", f"https://{__Host}/x/web-interface/nav")
        self.recent_url = ("GET", f"https://{__Host}/x/garb/rank/fan/recent")
        self.create_url = ("POST", f"https://{__Host}/x/garb/v2/trade/create")
        self.list_url = ("GET", f"https://{__Host}/x/garb/order/list")

        # 默认访问头
        self.headers.update({"Accept": "application/json, text/plain, */*"})
        self.headers.update({"Accept-Encoding": "gzip"})
        self.headers.update({"User-Agent": str(self._BiliUserAgent(**kwargs))})
        self.headers.update({"APP-KEY": "android"})
        self.headers.update({"env": "prod"})
        self.headers.update({"native_api_from": "h5"})
        self.headers.update({"x-bili-aurora-eid": str(__BiliEid)})
        self.headers.update({"x-bili-aurora-zone": ""})
        self.headers.update({"x-bili-mid": str(self.UserId)})
        self.headers.update({"Connection": "Keep-Alive"})
        self.headers.update({"Host": str(__Host)})

    @staticmethod
    def _BiliStatistics(version):
        __statistics = '{"appId":1,"platform":3,"version":"__version__","abtest":""}'
        return __statistics.replace("__version__", str(version))

    @staticmethod
    def _BiliTraceId():
        back6 = hex(round(time.time() / 256))
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
        form_data_ = form_data + f"&sign={sign}"
        return form_data_, len(form_data_)

    @staticmethod
    def _BiliUserAgent(**kwargs):
        system_version: str = kwargs.get("system_version")
        channel: str = kwargs.get("channel")
        sdk_int: str = kwargs.get("sdk_int")
        version: str = kwargs.get("version")
        buv_id: str = kwargs.get("buv_id")
        phone: str = kwargs.get("phone")
        build: str = kwargs.get("build")

        user_agent_list = [
            f"Mozilla/5.0 (Linux; Android {system_version}; {phone} Build/QP1A.190711.020; wv)",
            f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36",
            f"os/android model/{phone} build/{build} osVer/{system_version} sdkInt/{sdk_int}",
            f"network/2 BiliApp/{build} mobi_app/android channel/{channel} Buvid/{buv_id}",
            f"innerVer/{build} c_locale/zh_CN s_locale/zh_CN disable_rcmd/0 {version}",
            f"os/android model/{phone} mobi_app/android build/{build}",
            f"channel/{channel} innerVer/{build} osVer/{system_version} network/2"
        ]
        return " ".join(user_agent_list)


class FormData(BiliSession):
    def __init__(self, **kwargs):
        super(FormData, self).__init__(**kwargs)
        self.access_key = kwargs.get("access_key")
        assert self.access_key, "access_key not in kwargs"
        self.item_id = kwargs.get("item_id")
        assert self.item_id, "item_id not in kwargs"
        self.app_key = kwargs.get("app_key", "1d8b6e7d45233436")

    def FormDataUnpaid(self):
        form_data = urlencode({
            "access_key": str(self.access_key),
            "appkey": str(self.app_key),
            "csrf": str(self.BiliCsrf),
            "disable_rcmd": "0",
            "item_id": str(self.item_id),
            "statistics": str(self.statistics),
            "ts": str(round(time.time()))
        })
        return self._BiliAddFormDataSign(form_data)

    def FormDataDetail(self):
        form_data = urlencode({
            "access_key": str(self.access_key),
            "appkey": str(self.app_key),
            "csrf": str(self.BiliCsrf),
            "disable_rcmd": "0",
            "from": "",
            "from_id": "",
            "item_id": str(self.item_id),
            "part": "suit",
            "statistics": str(self.statistics),
            "ts": str(round(time.time()))
        })
        return self._BiliAddFormDataSign(form_data)

    def FormDataNav(self):
        form_data = urlencode({
            "access_key": str(self.access_key),
            "appkey": str(self.app_key),
            "csrf": str(self.BiliCsrf),
            "disable_rcmd": "0",
            "statistics": str(self.statistics),
            "ts": str(round(time.time()))
        })
        return self._BiliAddFormDataSign(form_data)

    def FormDataRecent(self):
        form_data = urlencode({
            "access_key": str(self.access_key),
            "appkey": str(self.app_key),
            "csrf": str(self.BiliCsrf),
            "disable_rcmd": "0",
            "item_id": str(self.item_id),
            "statistics": str(self.statistics),
            "ts": str(round(time.time()))
        })
        return self._BiliAddFormDataSign(form_data)

    def FormDataCreate(self, buy_num, add_month="-1"):
        form_data = urlencode({
            "access_key": str(self.access_key),
            "add_month": str(add_month),
            "appkey": str(self.app_key),
            "buy_num": str(buy_num),
            "coupon_token": "",
            "csrf": str(self.BiliCsrf),
            "currency": "bp",
            "disable_rcmd": "0",
            "f_source": "shop",
            "from": "search.list",
            "from_id": "",
            "item_id": str(self.item_id),
            "platform": "android",
            "statistics": str(self.statistics),
            "ts": str(round(time.time()))
        })
        return self._BiliAddFormDataSign(form_data)

    def FormDataList(self, pn=1, state=1):
        form_data = urlencode({
            "access_key": str(self.access_key),
            "appkey": str(self.app_key),
            "csrf": str(self.BiliCsrf),
            "disable_rcmd": "0",
            "pn": str(pn),
            "state": str(state),
            "statistics": str(self.statistics),
            "ts": str(round(time.time()))
        })
        return self._BiliAddFormDataSign(form_data)

    def FormDataCancel(self, order_id):
        form_data = urlencode({
            "access_key": str(self.access_key),
            "appkey": str(self.app_key),
            "csrf": str(self.BiliCsrf),
            "disable_rcmd": "0",
            "order_id": str(order_id),
            "statistics": str(self.statistics),
            "ts": str(round(time.time()))
        })
        return self._BiliAddFormDataSign(form_data)


class Headers(FormData):
    def __init__(self, **kwargs):
        super(Headers, self).__init__(**kwargs)

    def HeadersUnpaid(self):
        header = self.headers.copy()
        params = f"?navhide=1&from=search.list&id={self.item_id}&f_source=shop&native.theme=1"
        __referer = f"https://www.bilibili.com/h5/mall/suit/detail{params}"
        header.update({"Content-Type": "application/json"})
        header.update({"Referer": str(__referer)})
        header.update({"x-bili-trace-id": str(self._BiliTraceId())})
        return header

    def HeadersDetail(self):
        header = self.headers.copy()
        params = f"?navhide=1&from=search.list&id={self.item_id}&f_source=shop&native.theme=1"
        __referer = f"https://www.bilibili.com/h5/mall/suit/detail{params}"
        header.update({"Content-Type": "application/json"})
        header.update({"Referer": str(__referer)})
        header.update({"x-bili-trace-id": str(self._BiliTraceId())})
        return header

    def HeadersNav(self):
        header = self.headers.copy()
        params = f"?navhide=1&from=search.list&id={self.item_id}&f_source=shop&native.theme=1"
        __referer = f"https://www.bilibili.com/h5/mall/suit/detail{params}"
        header.update({"Content-Type": "application/json"})
        header.update({"Referer": str(__referer)})
        header.update({"x-bili-trace-id": str(self._BiliTraceId())})
        return header

    def HeadersRecent(self):
        header = self.headers.copy()
        params = f"?navhide=1&from=search.list&id={self.item_id}&f_source=shop&native.theme=1"
        __referer = f"https://www.bilibili.com/h5/mall/suit/detail{params}"
        header.update({"Content-Type": "application/json"})
        header.update({"Referer": str(__referer)})
        header.update({"x-bili-trace-id": str(self._BiliTraceId())})
        return header

    def HeadersCreate(self, content_len):
        header = self.headers.copy()
        params = f"?navhide=1&from=search.list&id={self.item_id}&f_source=shop&native.theme=1"
        __referer = f"https://www.bilibili.com/h5/mall/suit/detail{params}"
        header.update({"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        header.update({"Content-Length": str(content_len)})
        header.update({"Referer": str(__referer)})
        header.update({"x-bili-trace-id": str(self._BiliTraceId())})
        return header

    def HeadersList(self):
        header = self.headers.copy()
        __referer = f"https://www.bilibili.com/h5/mall/v2/order?navhide=1"
        header.update({"Content-Type": "application/json"})
        header.update({"Referer": str(__referer)})
        header.update({"x-bili-trace-id": str(self._BiliTraceId())})
        return header


class RequestTools(Headers):
    def SuitUnpaid(self):
        kwargs = {
            "params": self.FormDataUnpaid()[0],
            "headers": self.HeadersUnpaid()
        }
        response = self.request(*self.unpaid_url, **kwargs)
        return response.json()

    def SuitDetail(self):
        kwargs = {
            "params": self.FormDataDetail()[0],
            "headers": self.HeadersDetail()
        }
        response = self.request(*self.detail_url, **kwargs)
        return response.json()

    def SuitNav(self):
        kwargs = {
            "params": self.FormDataNav()[0],
            "headers": self.HeadersNav()
        }
        response = self.request(*self.nav_url, **kwargs)
        return response.json()

    def SuitRecent(self):
        kwargs = {
            "params": self.FormDataRecent()[0],
            "headers": self.HeadersRecent()
        }
        response = self.request(*self.recent_url, **kwargs)
        return response.json()

    def SuitCreate(self, buy_num, add_month="-1"):
        form_data, content_len = self.FormDataCreate(buy_num, add_month)
        kwargs = {
            "data": form_data, "headers": self.HeadersCreate(content_len)
        }
        response = self.request(*self.create_url, **kwargs)
        return response.json()

    def SuitList(self, pn=1, state=1):
        kwargs = {
            "params": self.FormDataList(pn, state)[0],
            "headers": self.HeadersList()
        }
        response = self.request(*self.list_url, **kwargs)
        return response.json()


class SuitTools(RequestTools):
    def __init__(self, **kwargs):
        super(SuitTools, self).__init__(**kwargs)

    def test(self):
        print(self.SuitUnpaid())
        print(self.SuitDetail())
        print(self.SuitNav())
        print(self.SuitRecent())
        print(self.SuitCreate(1))
        print(self.SuitList())

    def run(self):
        self.handle()

    def handle(self):
        ...


def main():
    from config import a_config

    suit_tools = SuitTools(**a_config)
    # suit_tools.test()
    # suit_tools.run()


if __name__ == '__main__':
    main()
