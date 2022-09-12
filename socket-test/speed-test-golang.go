package main

import (
	"fmt"
	"net"
	"time"
)

// 没有class真的很难受

func main() {
	client, _ := net.Dial("tcp", "api.bilibili.com:80")
	var message string = "GET https://api.bilibili.com/x/report/click/now HTTP/1.1\r\nHost: api.bilibili.com\r\nConnection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33\n\r\nAccept: text/html\r\nAccept-Encoding: gzip, deflate\r\n\r\n"
	time.Sleep(5 * time.Second)
	var StartTime int64 = time.Now().UnixNano() / 1e6
	var result = make([]byte, 4096)
	var _, _ = client.Write([]byte(message))
	_, _ = client.Read(result)
	fmt.Printf("%v\n", string(result))
	var EndTime int64 = time.Now().UnixNano() / 1e6
	_ = client.Close()
	fmt.Printf("耗时:%vms\n", EndTime-StartTime)
}
