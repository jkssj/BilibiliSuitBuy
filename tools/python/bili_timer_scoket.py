from typing import Union
import socket
import json
import time
import ssl

DefaultUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"


class BiliTimer(object):
    def __init__(self, sale_time: Union[float, int], **kwargs):

        self._host = kwargs.get("host", "api.bilibili.com")
        _user_agent = kwargs.get("user_agent", DefaultUserAgent)

        self.client = ssl.wrap_socket(socket.socket())

        self.sale_time = sale_time

        _message = f"GET https://{self._host}/x/report/click/now HTTP/1.1\r\n"
        _message += f"host: {self._host}\r\nConnection: keep-alive\r\n"
        _message += f"User-Agent: {_user_agent}\r\n\r\n"
        self.message = _message.encode()

    def GetBiliTime(self):
        self.client.sendall(self.message)
        body = self.client.read().split(b"\r\n\r\n")[-1]
        body_json = json.loads(body.decode())
        return int(body_json["data"]["now"])

    def WaitSeverTime(self, time_sleep=0.02):
        self.client.connect((self._host, 443))
        now_time = self.GetBiliTime()
        while self.sale_time >= now_time:
            now_time = self.GetBiliTime()
            time.sleep(time_sleep)
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
