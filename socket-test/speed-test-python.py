import socket
import time
import ssl


def main():
    message = "GET https://api.bilibili.com/x/report/click/now HTTP/1.1\r\nHost: api.bilibili.com\r\nConnection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33\n\r\nAccept: text/html\r\nAccept-Encoding: gzip, deflate\r\n\r\n"
    client = ssl.wrap_socket(socket.socket())
    client.connect(("api.bilibili.com", 443))
    start_time = time.time() * 1000
    client.send(message.encode())
    result = client.recv(4096)
    end_time = time.time() * 1000
    print(result.decode())
    print(f"耗时:{end_time - start_time}ms")


if __name__ == '__main__':
    main()
