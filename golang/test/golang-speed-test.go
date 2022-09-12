package main

import (
	"fmt"
	"net"
	"time"
)

func main() {
	var message string = "GET https://api.bilibili.com/x/report/click/now HTTP/1.1\r\nHost: api.bilibili.com\r\nConnection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33\r\nAccept: text/html\r\nAccept-Encoding: gzip, deflate\r\n\r\n"
	client, _ := net.Dial("tcp", "api.bilibili.com:80")
	var result []uint8 = make([]byte, 4096)
	time.Sleep(2 * time.Second)
	var StartTime int64 = time.Now().UnixNano() / 1e6
	var _, _ = client.Write([]byte(message))
	_, _ = client.Read(result)
	var EndTime int64 = time.Now().UnixNano() / 1e6
	_ = client.Close()
	fmt.Printf("%v\n", string(result))
	fmt.Printf("耗时:%vms\n", EndTime-StartTime)
}
