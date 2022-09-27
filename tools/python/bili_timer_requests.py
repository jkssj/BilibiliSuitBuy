from typing import Union
import requests
import time

DefaultHeaders = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}


class BiliTimer(requests.Session):
    sever_time_url = ("GET", "http://api.bilibili.com/x/report/click/now")

    def __init__(self, sale_time: Union[float, int], **kwargs):
        super(BiliTimer, self).__init__()
        self.trust_env = kwargs.get('trust_env', False)
        self.proxies = kwargs.get('proxies', None)

        self.headers.update(DefaultHeaders)
        self.headers.update(kwargs.get('headers', dict()))

        self.sale_time = sale_time

    def GetBiliTime(self):
        response = self.request(*self.sever_time_url)
        return int(response.json()["data"]["now"])

    def WaitSeverTime(self, time_sleep=0.02):
        now_time = self.GetBiliTime()
        while self.sale_time >= now_time:
            time.sleep(time_sleep)
            now_time = self.GetBiliTime()
        return now_time

    def WaitLocalTime(self, jump_time: int):
        now_time = time.time()
        jump_to_time = self.sale_time - jump_time
        while jump_to_time >= now_time:
            now_time = time.time()
            print(f"\r{now_time}", end="")
            time.sleep(0.001)
        return jump_to_time


def main():
    sale_time = time.time() + 10

    bili_timer = BiliTimer(sale_time)

    bili_timer.WaitLocalTime(3)  # 等待本地跳出, 提前3秒

    ...

    bili_timer.WaitSeverTime(0.02)  # 等待服务器跳出, 每次请求间隔0.02秒

    ...


if __name__ == '__main__':
    main()
