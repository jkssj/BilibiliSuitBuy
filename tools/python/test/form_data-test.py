import hashlib
import time
from urllib.parse import urlencode


# build 影响短链生成

# bili_local_id
# brand
# buvid
# channel
# cpu
# device
# device_id
# device_name
# device_platform
# device_tourist_id
# explor_attr
# extend

form_data = {
    "appkey": "4409e2ce8ffd12b8",
    # "bili_local_id": "fkZxFHEQJxQsHSlKNko2AGJWZF1tDGgLMgY_B2QFYw",
    # "brand": "samsung",
    "build": "105301",
    # "buvid": "XY30A9D303849C51D0D6F863F84A269E887E8",
    # "channel": "master",
    # "cpu": "qcom",
    # "device": "samsung",
    # "device_id": "fkZxFHEQJxQsHSlKNko2AGJWZF1tDGgLMgY_B2QFYw",
    # "device_name": "x1q",
    # "device_platform": "Android9samsungSM-G9810",
    # "device_tourist_id": "2788075357146",
    # "explor_attr": "0",
    # "extend": '{"option":"4"}',
    # "fingerprint": "202209231416342c59b10f56472a1b8562e726ed7d0cf268b462c38a73e88b",
    # "fourk": "0",
    # "gourl": "",
    # "guest_access_key": "GT_2788075357146",
    # "guest_id": "2788075357146",
    # "guid": "XY30A9D303849C51D0D6F863F84A269E887E8",
    # "local_fingerprint": "202209231416342c59b10f56472a1b8562e726ed7d0cf268b462c38a73e88b",
    "local_id": "XY30A9D303849C51D0D6F863F84A269E887E8",
    # "login_session_id": "9856482244a1fea7abbc4c23526ae97c",
    # "memory": "3941",
    # "mobi_app": "android_tv_yst",
    # "mode_switch": "true",
    # "model": "SM-G9810",
    # "mpi_id": "",
    # "mpi_model": "samsung_SM-G9810",
    # "mpi_type": "",
    # "networkstate": "wifi",
    # "platform": "android",
    # "resource_id": "",
    # "spm_id": "ott-platform.ott-me.me-all.all.click",
    # "statistics": '{"appId":"18","platform":"3","version":"105301"}',
    # "sys_ver": "28",
    # "teenager_mode": "1",
    "ts": str(round(time.time())),
    # "tv_brand": "master",
    # "uid": "0"
}


# f492b2ec5c2ed91217ab8205f5df1f39


app_sec = "59b43e04ad6965f34319062b478f83dd"

fdata = urlencode(form_data)

data = urlencode(form_data) + app_sec

sign = hashlib.md5(data.encode()).hexdigest()
form_data.update({"sign": sign})

header = {
    "User-Agent": "Mozilla/5.0 BiliTV/1.5.3.1 os/android model/SM-G9810 mobi_app/android_tv_yst build/105301 channel/master innerVer/105301 osVer/9 network/2",
    "Accept-Encoding": "gzip",
    "Content-Length": str(len(fdata + f"&sign={sign}")),
    "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    "Connection": "Keep-Alive",
    "Host": "passport.snm0516.aisee.tv"
}

import requests

r = requests.post("https://passport.snm0516.aisee.tv/x/passport-tv-login/qrcode/auth_code", data=fdata + f"&sign={sign}", headers=header)
print(r.json())
