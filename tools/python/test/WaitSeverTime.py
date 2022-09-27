import requests
import time

DefaultHeaders = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}


class TimeSession(requests.Session):
    sever_time_url = ("GET", "http://api.bilibili.com/x/report/click/now")

    def __init__(self, **kwargs):
        super(TimeSession, self).__init__()
        self.trust_env = kwargs.get('trust_env', False)
        self.proxies = kwargs.get('proxies', None)

        self.headers.update(DefaultHeaders)
        self.headers.update(kwargs.get('headers', dict()))

    def GetBiliTime(self):
        response = self.request(*self.sever_time_url)
        return int(response.json()["data"]["now"])

    def test(self, max_number=5):
        time_consuming_list = list()
        for i in range(max_number):
            s = time.time()
            bili_time = self.GetBiliTime()
            e = time.time()
            print(i, bili_time)
            time_consuming_list.append(e - s)
        all_time_consuming = sum(time_consuming_list)
        return all_time_consuming / len(time_consuming_list)
