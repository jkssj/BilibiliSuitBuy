from urllib.parse import urlsplit
from urllib.parse import unquote
from urllib.parse import quote
import tkinter.messagebox
import json
import uuid
import time
import os
import re

from application.module.decoration import (
    application_error,
    application_thread
)

from application.net.utils import (
    get_versions,
    get_sale_time,
    MobiAPP_ANDROID
)

from application.utils import (
    openFileAsk,
    reader_setting,
    parse_cookies,
    get_all_value,
    build_sign,
    SEC_ANDROID,
    build_x_bili_aurora_eid,
    build_x_bili_trace_id,
    get_sdk_int
)

from application.apps.windows import QrWindow


@application_thread
@application_error
def get_app_version(master) -> None:
    code, name = get_versions(MobiAPP_ANDROID)
    master["version_code"].writer(code)
    master["version_name"].writer(name)


@application_thread
@application_error
def open_old_setting(master) -> None:
    file_path = openFileAsk("打开旧配置", [("json", "*.json")], False)
    old_settings = reader_setting(file_path)["setting"]
    old_settings.pop("start_time")
    for key, value in old_settings.items():
        master[key].writer(str(value))


@application_thread
@application_error
def import_message(master) -> None:
    file_path = openFileAsk("导入报文", [("text", "*.txt")], False)
    with open(os.path.abspath(file_path), "rb") as f:
        content = f.read()
    f.close()

    message_content: list = content.split(b"\r\n")
    request: list = message_content[0].split(b" ")
    url_query: bytes = urlsplit(request[1]).query
    p = [i.split(b"=") for i in url_query.split(b"&")]
    p2 = [[ii.decode() for ii in i] for i in p]
    params = {unquote(i[0]): unquote(i[1]) for i in p2}
    headers_content = message_content[1:len(message_content) - 2]
    h = [i.split(b": ") for i in headers_content]
    h2h = [i if len(i) == 2 else [i[0], b""] for i in h]
    h3 = [[ii.decode() for ii in i] for i in h2h]
    headers = {unquote(i[0]).lower(): i[1] for i in h3}
    user_agent = headers["user-agent"]

    android_model_list = re.findall(r"model/.+? ", user_agent)
    android_model = android_model_list[0][6:][:-1]
    android_build_list = re.findall(r"osVer/.+? ", user_agent)
    android_build = android_build_list[0][6:][:-1]
    app_code_list = re.findall(r"build/.+? ", user_agent)
    version_code = app_code_list[0][6:][:-1]
    app_name_list = re.findall(r"disable_rcmd/0 .+? ", user_agent)
    version_name = app_name_list[0].split(" ")[1]
    cookies = parse_cookies(headers["cookie"])

    master["item_id"].writer(params["item_id"])
    master["buvid"].writer(cookies["Buvid"])
    master["android_model"].writer(android_model)
    master["android_build"].writer(android_build)
    master["version_code"].writer(version_code)
    master["version_name"].writer(version_name)
    master["cookie"].writer(headers["cookie"])
    master["access_key"].writer(params["access_key"])


@application_thread
@application_error
def import_login_sign(master) -> None:
    file_path = openFileAsk("导入登录标识", [("json", "*.json")], False)
    login_content = reader_setting(file_path)
    master["cookie"].writer(login_content["cookie"])
    master["access_key"].writer(login_content["access_key"])


@application_thread
@application_error
def save_login_sign(master):
    values = get_all_value(master, ["cookie", "access_key"], True)
    file_path = openFileAsk("保存登录标识", [("json", "*.json")], True)
    with open(file_path.name, "w", encoding="utf-8") as f:
        content = {
            "cookie": values["cookie"],
            "access_key": values["access_key"]
        }
        f.write(json.dumps(content))
    f.close()
    tkinter.messagebox.showinfo("提示", "保存完成")


@application_thread
@application_error
def qrcode_login(master):
    values = get_all_value(master, ["android_model", "android_build", "buvid"], True)
    login_box = QrWindow(values["android_model"], values["android_build"], values["buvid"])
    while master.winfo_exists() and login_box.winfo_exists():
        code, data = login_box.login.Verify(login_box.auth_code)
        if code == 0:
            access_key, cookie_text = login_box.login.Extract(data)
            master["cookie"].writer(cookie_text)
            master["access_key"].writer(access_key)
            break
        if code == 86038:
            raise Exception("二维码已失效")
        time.sleep(login_box.update_time)
    login_box.destroy()


@application_thread
@application_error
def save_setting(master) -> None:
    """ 保存整个配置 """
    setting_config = reader_setting("./settings/setting.json")

    settings = get_all_value(master, ["coupon_token", "delay_time"], False)
    settings["coupon_token"] = master["coupon_token"].value(False) or str()
    settings["delay_time"] = master["delay_time"].number(False) or int(0)

    if setting_config["sale_time"] is None:
        start_time = get_sale_time(settings["item_id"])
    else:
        start_time = int(setting_config["sale_time"])
    settings["start_time"] = int(start_time)

    __statistics = '{"appId":1,"platform":3,"version":"__ver__","abtest":""}'
    __statistics = __statistics.replace("__ver__", settings["version_name"])
    __cookie = parse_cookies(settings["cookie"])
    __eid = build_x_bili_aurora_eid(__cookie["DedeUserID"])
    __trace_id = build_x_bili_trace_id(start_time)

    form_data_format = reader_setting("./settings/content/form_data.json")["android"]
    user_agent_format = reader_setting("./settings/content/user_agent.json")["android"]
    form_data_text = form_data_format.format(
        ACCESS_KEY=settings["ACCESS_KEY".lower()],
        ADD_MONTH=settings["ADD_MONTH".lower()],
        BUY_NUM=settings["BUY_NUM".lower()],
        COUPON_TOKEN=settings["COUPON_TOKEN".lower()],
        F_SOURCE=settings["F_SOURCE".lower()],
        SHOP_FROM=settings["SHOP_FROM".lower()],
        ITEM_ID=settings["ITEM_ID".lower()],
        STATISTICS=quote(__statistics),
        CSRF=__cookie["bili_jct"],
        TS=str(start_time)
    )

    user_agent = user_agent_format.format(
        ANDROID_BUILD=settings["ANDROID_BUILD".lower()],
        ANDROID_MODEL=settings["ANDROID_MODEL".lower()],
        ANDROID_BUILD_M=setting_config["BUILD_M".lower()],
        BUVID=settings["BUVID".lower()],
        SDK_INT=get_sdk_int(settings["ANDROID_BUILD".lower()]),
        VERSION_CODE=settings["VERSION_CODE".lower()],
        CHANNEL=setting_config["CHANNEL".lower()],
        SESSION_ID=str(uuid.uuid4()).replace("-", "")[:8],
        VERSION_NAME=settings["VERSION_NAME".lower()]
    )

    __referer = setting_config["referer"].format(
        F_SOURCE=settings["F_SOURCE".lower()],
        SHOP_FROM=settings["SHOP_FROM".lower()],
        ID=settings["item_id"]
    )

    sign = build_sign(form_data_text, SEC_ANDROID)
    form_data = form_data_text + f"&sign={sign}"

    headers: dict = setting_config["headers"]
    headers.update({"content-length": str(len(form_data))})
    headers.update({"cookie": settings["cookie"]})
    headers.update({"buvid": settings["buvid"]})
    headers.update({"x-bili-aurora-eid": __eid})
    headers.update({"x-bili-mid": __cookie["DedeUserID"]})
    headers.update({"x-bili-trace-id": __trace_id})
    headers.update({"referer": __referer})
    headers.update({"host": setting_config["host"]})
    headers.update({"user-agent": user_agent})

    file_path = openFileAsk("保存", [("json", "*.json")], True)
    with open(file_path.name, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "setting": settings,
            "form_data": form_data,
            "headers": headers,
        }))
    f.close()

    tkinter.messagebox.showinfo("提示", "保存完成")


# 是这样的, 没有错的
func_list = [
    (get_app_version, "get_app_version"),
    (open_old_setting, "open_old_setting"),
    (import_message, "import_message"),
    (import_login_sign, "import_login_sign"),
    (save_login_sign, "save_login_sign"),
    (qrcode_login, "qrcode_login"),
    (save_setting, "save_setting")
]
