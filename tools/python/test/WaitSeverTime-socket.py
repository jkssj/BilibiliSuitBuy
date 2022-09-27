import socket
import json
import ssl


message = b"GET https://api.bilibili.com/x/report/click/now HTTP/1.1\r\nhost: api.bilibili.com\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0\r\n\r\n"

client = ssl.wrap_socket(socket.socket())
client.connect(("api.bilibili.com", 443))

for i in range(99):
    client.sendall(message)

    response = client.read().split(b"\r\n\r\n")[-1]
    now_time = json.loads(response.decode())["data"]["now"]

    print(f"\r{i}/{now_time}", end="")

client.close()
