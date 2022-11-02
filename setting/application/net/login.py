from urllib.parse import urlencode
import time

from application.utils import reader_setting
from application.utils import build_sign, SEC_TV

from application.net.session import Connect
from application.net.utils import get_versions, MobiAPP_TV


class LoginQrcode(Connect):
    def __init__(self, model: str, os_ver: str, buvid: str):
        super(LoginQrcode, self).__init__()

        login_config = reader_setting("./settings/net/login.json")
        user_agent_format = reader_setting("./settings/content/user_agent.json")

        if login_config["version"] == "auto":
            self.build, version = get_versions(MobiAPP_TV)
        else:
            self.build, version = tuple(login_config["version"])

        user_agent = user_agent_format["tv"].format(
            TV_CODE=self.build, CHANNEL=login_config["channel"],
            TV_NAME=version, ANDROID_MODEL=model,
            ANDROID_BUILD=os_ver
        )

        self.short_url = login_config["short_url"]
        self.login_host = login_config["host"]
        self.app_key = login_config["appkey"]
        self.buvid = buvid

        self.headers.update(login_config["headers"])
        self.headers.update({"User-Agent": user_agent})
        self.headers.update({"Buvid": str(self.buvid)})

    def GetUrlAndAuthCode(self) -> tuple[str, str]:
        """ 获取登录链接加标识 """
        form_data = {
            "appkey": self.app_key,
            "local_id": str(self.buvid),
            "ts": str(round(time.time()))
        }
        if self.short_url:
            form_data.update({"build": self.build})
        sorted_key = sorted(form_data)
        form_data = {i: form_data[i] for i in sorted_key}
        form_data_text = urlencode(form_data)
        sign = build_sign(form_data_text, SEC_TV)
        form_data = form_data_text + f"&sign={sign}"
        self.headers.update({"Content-Length": str(len(form_data))})
        url = f"https://{self.login_host}/x/passport-tv-login/qrcode/auth_code"
        response = self.request_X("POST", url, data=form_data)
        auth_code = response.json()["data"]["auth_code"]
        login_url = response.json()["data"]["url"]
        return str(login_url), str(auth_code)

    def Verify(self, auth_code: str) -> tuple[dict, int]:
        form_data = urlencode({
            "appkey": self.app_key,
            "auth_code": str(auth_code),
            "local_id": str(self.buvid),
            "ts": str(round(time.time()))
        })
        form_data_sign = build_sign(form_data, SEC_TV)
        form_data = form_data + f"&sign={form_data_sign}"
        self.headers.update({"Content-Length": str(len(form_data))})
        url = f"https://{self.login_host}/x/passport-tv-login/qrcode/poll"
        response = self.request_X("POST", url, data=form_data)
        return response.json()["code"], response.json()

    def Extract(self, response_json: dict) -> tuple[str, str]:
        """ 提取cookie, access_key """
        access_key = str(response_json["data"]["access_token"])
        cookie_list = response_json["data"]["cookie_info"]["cookies"]
        cookie_dict = {li["name"]: li["value"] for li in cookie_list}
        cookie_dict.update({"Buvid": str(self.buvid)})
        cookie_list = [f"{k}={v}" for k, v in cookie_dict.items()]
        return access_key, "; ".join(cookie_list)
