from urllib.parse import urlencode
import requests
import hashlib
import random
import qrcode
import time
import sys
import os


class LoginSession(requests.Session):
    def __init__(self, **kwargs):
        super(LoginSession, self).__init__()

        self.__host = kwargs.get("host", "passport.bilibili.com")

        self.max_retry: int = kwargs.get("max_retry", 5)
        self.timeout: int = kwargs.get("timeout", 5)

        self.auth_code_url = ("POST", f"https://{self.__host}/x/passport-tv-login/qrcode/auth_code")
        self.poll_rul = ("POST", f"https://{self.__host}/x/passport-tv-login/qrcode/poll")

        self._Buvid = kwargs.get("buvid", self.RandomBuvid())

        self.headers.update({"Accept-Encoding": "gzip"})
        self.headers.update({"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.headers.update({"APP-KEY": "android_tv_yst"})
        self.headers.update({"Buvid": str(self._Buvid)})

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

    @staticmethod
    def GetTokenAndCookie(verify_data: dict):
        ...


def main():
    login_module = BiliLogin()
    login_url, auth_code = login_module.GetUrlAndAuthCode()
    qrcode_img = qrcode.make(login_url)
    qrcode_img.save(f"./{auth_code}.png")

    print("-" * 30)
    print(os.path.abspath(f"./{auth_code}.png"))
    print(login_url)
    print("-" * 30)

    while True:
        verify_data = login_module.GetVerifyContent(auth_code)
        if verify_data["code"] == 0:
            login_module.GetTokenAndCookie(verify_data)
            break
        time.sleep(5)


if __name__ == '__main__':
    main()
