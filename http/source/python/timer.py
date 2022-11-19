import socket
import json
import time
import ssl

host = "api.bilibili.com"

message_list = [
    f"GET /x/report/click/now HTTP/1.1", f"host: {host}", "Connection: keep-alive",
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
]

http_message = str("\r\n".join(message_list) + "\r\n\r\n").encode()


class BiliTimer(object):
    def __init__(self, sale_time: int, delay_time: int):
        super(BiliTimer, self).__init__()
        self.sale_time = float(sale_time)
        self.delay_time = delay_time / 1000
        self.client = None

    def updateClient(self, **kwargs):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.purpose = ssl.Purpose.SERVER_AUTH
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_default_certs()
        connection = socket.create_connection((host, 443))
        kwargs.update({"server_hostname": host})
        self.client = context.wrap_socket(connection, **kwargs)

    def GetBiliTime(self):
        self.client.sendall(http_message)
        rec = self.client.read()
        if rec == b"":
            self.updateClient()
            return self.GetBiliTime()
        body = rec.split(b"\r\n\r\n")[-1]
        body_json = json.loads(body.decode())
        return int(body_json["data"]["now"])

    def WaitLocalTime(self, jump_time: int):
        now_time = time.time()
        jump_to_time = self.sale_time - jump_time
        while jump_to_time > now_time:
            print(f"\r{now_time}", end="")
            now_time = time.time()
            time.sleep(0.001)
        return jump_to_time

    def WaitSeverTime(self):
        self.updateClient()
        now_time = self.GetBiliTime()
        while self.sale_time > now_time:
            print(f"\r{now_time}", end="")
            now_time = self.GetBiliTime()
        time.sleep(self.delay_time)
        return now_time
