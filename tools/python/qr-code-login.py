from urllib.parse import urlencode
import requests
import hashlib
import random
import qrcode
import time
import json
import sys
import os


DefaultHeader = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}


class LoginSession(requests.Session):
    def __init__(self, **kwargs):
        super(LoginSession, self).__init__()

        self.trust_env = kwargs.get("trust_env", False)
        self.proxies = kwargs.get("proxies", None)

        self.login_host = kwargs.get("headers", "passport.bilibili.com")
        self._Buvid = kwargs.get("buvid", self.RandomBuvid())

        self.headers.update(DefaultHeader)
        self.headers.update({"Accept-Encoding": "gzip"})
        self.headers.update({"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.headers.update({"APP-KEY": "android_tv_yst"})
        self.headers.update({"Buvid": str(self._Buvid)})

        self.auth_code_url = ("POST", f"https://{self.login_host}/x/passport-tv-login/qrcode/auth_code")
        self.poll_rul = ("POST", f"https://{self.login_host}/x/passport-tv-login/qrcode/poll")

        self.headers.update(kwargs.get("headers", dict()))

        self.max_retry: int = kwargs.get("max_retry", 5)
        self.timeout: int = kwargs.get("timeout", 5)

    @staticmethod
    def RandomBuvid():
        number = random.randrange(int("1" * 42), int("9" * 42))
        return "XY" + str(hex(number))[2:].upper()

    def Request(self, method, url, error=None, **kwargs):
        if "timeout" not in kwargs:
            kwargs.update({"timeout": self.timeout})
        for number in range(0, self.max_retry):
            try:
                response = self.request(method, url, **kwargs)
            except Exception as Error:
                error = Error
            else:
                return response
        sys.exit(error)

    def __del__(self):
        self.close()

    def SetUserAgent(self, mobi_app, model, channel):
        params = {"mobi_app": mobi_app}
        url = "https://app.bilibili.com/x/v2/version"
        response = self.Request("GET", url, params=params)
        if response.json()["code"] != 0:
            sys.exit(f"https://app.bilibili.com/x/v2/version?mobi_app={mobi_app}")
        mobi_app_data = response.json()["data"][0]
        __build = str(mobi_app_data["build"])
        __version = str(mobi_app_data["version"])
        user_agent_list = [
            f"Mozilla/5.0 BiliTV/{__version} os/android model/{model}",
            f"mobi_app/{mobi_app} build/{__build} channel/{channel}",
            f"innerVer/{__build} osVer/9 network/2"
        ]
        self.headers.update({"User-Agent": " ".join(user_agent_list)})
        return " ".join(user_agent_list)


class BiliLogin(LoginSession):
    def __init__(self, **kwargs):
        super(BiliLogin, self).__init__(**kwargs)

    @staticmethod
    def FormDataAddSign(form_data: str):
        app_sec = "59b43e04ad6965f34319062b478f83dd"
        data = form_data + app_sec
        sign = hashlib.md5(data.encode()).hexdigest()
        return form_data + "&sign=" + str(sign)

    def GetUrlAndAuthCode(self, build="105301"):
        __form_data = urlencode({
            "appkey": "4409e2ce8ffd12b8",
            "build": str(build),
            "local_id": str(self._Buvid),
            "ts": str(round(time.time()))
        })
        form_data = self.FormDataAddSign(__form_data)
        self.headers.update({"Content-Length": str(len(form_data))})
        response = self.Request(*self.auth_code_url, data=form_data)
        if response.json()["code"] != 0:
            sys.exit(f"code != 0")
        auth_code = response.json()["data"]["auth_code"]
        login_url = response.json()["data"]["url"]
        return login_url, auth_code

    def GetVerifyContent(self, auth_code):
        __form_data = urlencode({
            "appkey": "4409e2ce8ffd12b8",
            "auth_code": str(auth_code),
            "local_id": str(self._Buvid),
            "ts": str(round(time.time()))
        })
        form_data = self.FormDataAddSign(__form_data)
        self.headers.update({"Content-Length": str(len(form_data))})
        response = self.Request(*self.poll_rul, data=form_data)
        return response.json()

    def ExtractAccessTokenAndCookies(self, response_json: dict):
        mid = str(response_json["data"]["mid"])
        access_key = str(response_json["data"]["access_token"])
        cookie_list = response_json["data"]["cookie_info"]["cookies"]
        cookie_dict = {li["name"]: li["value"] for li in cookie_list}
        cookie_dict.update({"Buvid": str(self._Buvid)})
        return mid, access_key, cookie_dict

    def start(self, mobi_app="android_tv_yst", model="SM-G9810", channel="master"):
        self.SetUserAgent(mobi_app, model, channel)

        login_url, auth_code = self.GetUrlAndAuthCode()
        qrcode_img = qrcode.make(login_url)
        qrcode_img.save(f"./{auth_code}.png")

        print("-" * 30)
        print(os.path.abspath(f"./{auth_code}.png"))
        print(login_url)
        print("-" * 30)

        code = 86039
        response = self.GetVerifyContent(auth_code)
        print(response)
        while code != 0:
            time.sleep(5)
            response = self.GetVerifyContent(auth_code)
            code = int(response["code"])
            print(response)
        ages = self.ExtractAccessTokenAndCookies(response)
        mid, access_key, cookie_dict = ages

        with open(f"./{mid}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "mid": mid, "access_key": access_key, "cookies": cookie_dict
            }))
        f.close()

        print(os.path.abspath(f"./{mid}.json"))


def main():
    login = BiliLogin()
    login.start()


if __name__ == '__main__':
    main()
