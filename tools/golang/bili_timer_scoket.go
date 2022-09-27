package main

import (
	"encoding/json"
	"fmt"
	"net"
	"regexp"
	"strings"
	"time"
)

type BiliTimer struct {
	client   net.Conn
	SaleTime float64
	_host    string
	message  []byte
}

func (bili *BiliTimer) init(SaleTime float64, args map[string]string) *BiliTimer {
	var DefaultHost string = "api.bilibili.com"
	var DefaultUserAgent string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"

	var _Host string = args["host"]
	var _UserAgent string = args["user_agent"]

	if _Host == "" {
		_Host = DefaultHost
	}

	if _UserAgent == "" {
		_UserAgent = DefaultUserAgent
	}

	bili.SaleTime = SaleTime
	bili._host = _Host

	var message string = ""

	message += fmt.Sprintf("GET https://%v/x/report/click/now HTTP/1.1\r\n", bili._host)
	message += fmt.Sprintf("host: %v\r\nConnection: keep-alive\r\n", bili._host)
	message += fmt.Sprintf("User-Agent: %v\r\n\r\n", _UserAgent)

	bili.message = []byte(message)

	var Adder = fmt.Sprintf("%v:80", bili._host)
	var client, _ = net.Dial("tcp", Adder)
	bili.client = client

	return bili
}

func (bili *BiliTimer) GetBiliTime() float64 {
	var result []uint8 = make([]byte, 1024)
	var _, _ = bili.client.Write(bili.message)
	var _, _ = bili.client.Read(result)
	var res []string = strings.Split(string(result), "\r\n")
	var re_, _ = regexp.Compile("\\{.*}")
	var JsonData = make(map[string]map[string]int64)
	var body = re_.FindString(res[len(res)-1])
	var _ = json.Unmarshal([]byte(body), &JsonData)
	return float64(JsonData["data"]["now"])
}

func (bili *BiliTimer) WaitLocalTime(jump int64) {
	var NowTime, JumpTime float64
	NowTime = float64(time.Now().UnixNano()) / 1e9
	JumpTime = bili.SaleTime - float64(jump)
	for JumpTime >= NowTime {
		NowTime = float64(time.Now().UnixNano()) / 1e9
		fmt.Printf("\r%f", JumpTime-NowTime)
	}
}

func (bili *BiliTimer) WaitSeverTime(sleep float64) float64 {
	var NowTime float64 = bili.GetBiliTime()
	for bili.SaleTime >= NowTime {
		fmt.Printf("%f\n", NowTime)
		NowTime = bili.GetBiliTime()
		time.Sleep(time.Duration(sleep) * time.Second)
	}
	return NowTime
}

func main() {
	var config = map[string]string{}

	var SaleTime = float64(time.Now().Unix() + 10)

	var bili *BiliTimer = new(BiliTimer).init(SaleTime, config)

	// 等待本地跳出, 提前3秒
	bili.WaitLocalTime(3)

	// ...

	// 等待服务器跳出, 每次请求间隔0.02秒
	bili.WaitSeverTime(0.02)

	// ...
}
