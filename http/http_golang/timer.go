package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

type BiliTimer struct {
	SaleTime  float64
	DelayTime float64
	Message   []byte
	client    *tls.Conn
}

func (receiver *BiliTimer) init(SaleTime, DelayTime int64) *BiliTimer {
	receiver.DelayTime = float64(DelayTime / 1000)
	receiver.SaleTime = float64(SaleTime)
	var MessageList = []string{
		"GET /x/report/click/now HTTP/1.1\r\nhost: api.bilibili.com", "Connection: keep-alive",
		"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
	}
	receiver.Message = []byte(strings.Join(MessageList, "\r\n") + "\r\n\r\n")
	return receiver
}

func (receiver *BiliTimer) updateClient() {
	receiver.client, _ = tls.Dial("tcp", "api.bilibili.com:443", &tls.Config{
		InsecureSkipVerify: true,
		ServerName:         "api.bilibili.com",
		MinVersion:         tls.VersionTLS12,
		MaxVersion:         tls.VersionTLS12,
		ClientAuth:         tls.RequireAndVerifyClientCert,
	})
}

func (receiver *BiliTimer) GetBiliTime() float64 {
	_, _ = receiver.client.Write(receiver.Message)
	var buf = make([]byte, 1024)
	var length, _ = receiver.client.Read(buf)
	var rec = string(buf[:length])
	if len(rec) == 0 {
		receiver.updateClient()
		return receiver.GetBiliTime()
	}
	var JsonData = make(map[string]map[string]int64)
	var SplitBody = strings.Split(rec, "\r\n\r\n")
	var Body = SplitBody[len(SplitBody)-1]
	var _ = json.Unmarshal([]byte(Body), &JsonData)
	return float64(JsonData["data"]["now"])
}

func (receiver *BiliTimer) WaitLocalTime(jump int64) float64 {
	var NowTime, JumpTime float64
	NowTime = float64(time.Now().UnixNano()) / 1e9
	JumpTime = receiver.SaleTime - float64(jump)
	for JumpTime > NowTime {
		fmt.Printf("\r%f", NowTime)
		NowTime = float64(time.Now().UnixNano()) / 1e9
	}
	return NowTime
}

func (receiver *BiliTimer) WaitSeverTime() float64 {
	var SleepTimeNumber = receiver.DelayTime * float64(time.Second)
	receiver.updateClient()
	var NowTime = receiver.GetBiliTime()
	for NowTime < receiver.SaleTime {
		fmt.Printf("\r%f", NowTime)
		NowTime = receiver.GetBiliTime()
	}
	time.Sleep(time.Duration(SleepTimeNumber))
	return NowTime
}
