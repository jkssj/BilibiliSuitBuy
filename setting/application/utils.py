from application.errors import (
    SdkIntIndexError, GuiFileAskWarning
)

import tkinter.filedialog
from typing import Union
import hashlib
import base64
import uuid
import json
import os

SEC_TV: str = "59b43e04ad6965f34319062b478f83dd"
SEC_ANDROID: str = "560c52ccd288fed045859ed18bffd973"


def reader_setting(file_path: str, **kwargs) -> Union[dict, list]:
    """ 读取设置文件 """
    if "encoding" not in kwargs:
        kwargs.update({"encoding": "utf-8"})
    path = os.path.abspath(file_path)
    with open(path, "r", **kwargs) as f:
        data = json.loads(f.read())
    f.close()
    return data


def rgb_to_tkinter(rgb: tuple[int, int, int]) -> str:
    """ rgb格式转tkinter适配 """
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def get_sdk_int(build: str, sdk_int_file_path: str = None) -> str:
    """ 以系统版本获取sdk """
    if sdk_int_file_path:
        data = reader_setting(sdk_int_file_path)
    else:
        data = reader_setting("./settings/content/sdk_int.json")
    build_list = build.split(".")
    sdk_int = None
    for li in build_list:
        if li not in data:
            if sdk_int is not None:
                return str(sdk_int)
            raise SdkIntIndexError(f"未找到{build}的sdk_int")
        sdk_int = data[li]["value"]
        data = data[li]
    return str(sdk_int)


def get_all_value(master, no_items: list, reverse=False) -> dict:
    """
    获取所有内容
    no_items 不抛出异常的值
    reverse 反向选择 不抛出异常的值
    """
    entry_dict, return_dict = dict(), dict()
    for key, value in master.__dict__.items():
        if "_entry" in key:
            entry_dict[key.replace("_entry", "")] = value
    if reverse:
        reverse_no_items = list(entry_dict)
        for li in no_items:
            reverse_no_items.remove(li)
        no_items = reverse_no_items
    for key in entry_dict:
        err = False if key in no_items else f"{key}未填写"
        return_dict[key] = entry_dict.get(key).value(err)
    return return_dict


def openFileAsk(title: str, filetypes: list, save=False):
    """ 打开文件会话框 """
    kwargs = {"title": title, "filetypes": filetypes}
    if save:
        kwargs.update({"initialfile": "setting.json"})
        file_ack = tkinter.filedialog.asksaveasfile(**kwargs)
    else:
        file_ack = tkinter.filedialog.askopenfilename(**kwargs)
    if not file_ack:
        raise GuiFileAskWarning("文件会话框未选择")
    return file_ack


def parse_cookies(cookies_content: str) -> dict:
    """  cookie string to dict """
    c1: list = cookies_content.split("; ")
    c2 = [i.split("=") for i in c1]
    return {i[0]: i[1] for i in c2}


def build_sign(form_data: str, app_sec: str = SEC_ANDROID) -> str:
    """ 生成 表单最后的sign """
    form_data_sec = f"{form_data}{app_sec}"
    md5_hashlib = hashlib.md5()
    md5_hashlib.update(form_data_sec.encode())
    return md5_hashlib.hexdigest()


def build_x_bili_aurora_eid(mid: str):
    """ 生成 x-bili-aurora-eid """
    length = mid.__len__()
    barr = bytearray(length)
    if length - 1 < 0:
        return ""
    for i in range(length):
        s = ord("ad1va46a7lza"[i % 12])
        barr[i] = ord(mid[i]) ^ s
    return base64.b64encode(barr).decode()


def build_x_bili_trace_id(sela_time: Union[int, float]):
    """ 生成 x-bili-trace-id """
    back6 = hex(round(sela_time / 256))
    front = str(uuid.uuid4()).replace("-", "")
    _data1 = front[6:] + back6[2:]
    _data2 = front[22:] + back6[2:]
    return f"{_data1}:{_data2}:0:0"
