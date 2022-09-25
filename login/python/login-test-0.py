from urllib.parse import urlencode
import requests
import hashlib
import random
import qrcode
import time
import uuid
import sys
import os


class LoginSession(requests.Session):
    def __init__(self, **kwargs):
        super(LoginSession, self).__init__()

        self.__host = kwargs.get("host", "passport.bilibili.com")

        self.auth_code_url = ("POST", f"https://{self.__host}/x/passport-tv-login/qrcode/auth_code")
        self.poll_rul = ("POST", f"https://{self.__host}/x/passport-tv-login/qrcode/poll")

        self.__Buvid = kwargs.get("buvid", self.RandomBuvid())

        self.headers.update({"Accept-Encoding": "gzip"})
        self.headers.update({"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"})
        self.headers.update({"APP-KEY": "android_tv_yst"})
        self.headers.update({"Buvid": str(self.__Buvid)})
        self.headers.update({"env": "prod"})
        self.headers.update({"x-bili-aurora-eid": "0"})
        self.headers.update({"x-bili-aurora-zone": ""})

    @staticmethod
    def BiliTraceId():
        back6 = hex(round(time.time() / 256))
        front = str(uuid.uuid4()).replace("-", "")
        _data1 = front[6:] + back6[2:]
        _data2 = front[22:] + back6[2:]
        return f"{_data1}:{_data2}:0:0"

    @staticmethod
    def RandomBuvid():
        number = random.randrange(int("1" * 42), int("9" * 42))
        return "XY" + str(hex(number))[2:].upper()

    @staticmethod
    def FormDataAddSign(form_data: str):
        app_sec = "59b43e04ad6965f34319062b478f83dd"
        data = form_data + app_sec
        sign = hashlib.md5(data.encode()).hexdigest()
        return form_data + "&sign=" + str(sign)

    def GetLoginUrlAndLoginId(self, build="105301"):
        __form_data = urlencode({
            "appkey": "4409e2ce8ffd12b8",
            "build": str(build),
            "local_id": str(self.__Buvid),
            "ts": str(round(time.time()))
        })
        form_data = self.FormDataAddSign(__form_data)
        self.headers.update({"Content-Length": str(len(form_data))})
        self.headers.update({"x-bili-trace-id": self.BiliTraceId()})
        response = self.request(*self.auth_code_url, data=form_data)
        if response.json()["code"] != 0:
            sys.exit(f"code != 0")
        auth_code = response.json()["data"]["auth_code"]
        login_url = response.json()["data"]["url"]
        return login_url, auth_code

    def VerifyLogin(self, auth_code):
        __form_data = urlencode({
            "appkey": "4409e2ce8ffd12b8",
            "auth_code": str(auth_code),
            "local_id": str(self.__Buvid),
            "ts": str(round(time.time()))
        })
        form_data = self.FormDataAddSign(__form_data)
        self.headers.update({"Content-Length": str(len(form_data))})
        self.headers.update({"x-bili-trace-id": self.BiliTraceId()})
        response = self.request(*self.poll_rul, data=form_data)
        return response.json()


def main():
    login_module = LoginSession()
    login_url, auth_code = login_module.GetLoginUrlAndLoginId()
    qrcode_img = qrcode.make(login_url)
    qrcode_img.save(f"./{auth_code}.png")
    print("-" * 30)
    print(os.path.abspath(f"./{auth_code}.png"))
    print(login_url)
    print("-" * 30)
    while True:
        print(login_module.VerifyLogin(auth_code))
        time.sleep(5)


if __name__ == '__main__':
    main()
