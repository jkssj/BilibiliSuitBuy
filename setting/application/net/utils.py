from application.net.session import Connect

MobiAPP_TV: str = "android_tv_yst"
MobiAPP_ANDROID: str = "android"


def get_versions(mod: str = MobiAPP_ANDROID) -> tuple[str, str]:
    url = f"https://app.bilibili.com/x/v2/version"
    with Connect() as session:
        res = session.request("GET", url, params={"mobi_app": mod})
    build = str(res.json()["data"][0]["build"])
    version = str(res.json()["data"][0]["version"])
    return build, version


def get_sale_time(item_id: str) -> int:
    """ 获取开售时间 """
    url = f"https://api.bilibili.com/x/garb/v2/mall/suit/detail"
    with Connect() as session:
        res = session.request("GET", url, params={"item_id": item_id})
    return int(res.json()["data"]["properties"]["sale_time_begin"])
