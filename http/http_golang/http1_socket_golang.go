package main

import (
	"crypto/tls"
	"fmt"
	"os"
	"time"
)

// BuildMessage
// 生成报文
func BuildMessage(headers map[string]string, formData string) ([]byte, []byte) {
	var message = "POST /x/garb/v2/trade/create HTTP/1.1\r\n"
	message += fmt.Sprintf("native_api_from: %v\r\n", headers["native_api_from"])
	message += fmt.Sprintf("Cookie: %v\r\n", headers["cookie"])
	message += fmt.Sprintf("Buvid: %v\r\n", headers["buvid"])
	message += fmt.Sprintf("Accept: %v\r\n", headers["accept"])
	message += fmt.Sprintf("Referer: %v\r\n", headers["referer"])
	message += fmt.Sprintf("env: %v\r\n", headers["env"])
	message += fmt.Sprintf("APP-KEY: %v\r\n", headers["app-key"])
	message += fmt.Sprintf("User-Agent: %v\r\n", headers["user-agent"])
	message += fmt.Sprintf("x-bili-trace-id: %v\r\n", headers["x-bili-trace-id"])
	message += fmt.Sprintf("x-bili-aurora-eid: %v\r\n", headers["x-bili-aurora-eid"])
	message += fmt.Sprintf("x-bili-mid: %v\r\n", headers["x-bili-mid"])
	message += fmt.Sprintf("x-bili-aurora-zone: %v\r\n", headers["x-bili-aurora-zone"])
	message += fmt.Sprintf("Content-Type: %v\r\n", headers["content-type"])
	message += fmt.Sprintf("Content-Length: %v\r\n", headers["content-length"])
	message += fmt.Sprintf("Host: %v\r\n", headers["host"])
	message += fmt.Sprintf("Connection: %v\r\n", headers["connection"])
	message += fmt.Sprintf("Accept-Encoding: %v\r\n\r\n", headers["accept-encoding"])
	var MessageByte = []byte(message + formData)
	return MessageByte[:len(MessageByte)-1], MessageByte[len(MessageByte)-1:]
}

// H1CreateTlsConnection
// 创建连接
func H1CreateTlsConnection(BuyHost string) *tls.Conn {
	var adder = fmt.Sprintf("%v:443", BuyHost)
	var client, _ = tls.Dial("tcp", adder, &tls.Config{
		InsecureSkipVerify: false,
		ServerName:         BuyHost,
		MinVersion:         tls.VersionTLS12,
		MaxVersion:         tls.VersionTLS12,
		ClientAuth:         tls.RequireAndVerifyClientCert,
	})
	return client
}

// H1SendMessage
// 发送请求
func H1SendMessage(client *tls.Conn, body []byte) {
	_, _ = client.Write(body)
}

// H1ReceiveResponse
// 接收响应
func H1ReceiveResponse(client *tls.Conn, BufLen int64) []byte {
	var result = make([]byte, BufLen)
	var length, _ = client.Read(result)
	return result[:length]
}

func main() {
	var filePath = GetSettingFilePath()
	var headers, startTime, delayTime, formData = ReaderSetting(filePath)
	if startTime <= time.Now().Unix() {
		var code string
		fmt.Printf("启动时间小于当前时间, 是否继续[y/n]:")
		_, _ = fmt.Scan(&code)
		if code != "y" {
			os.Exit(1)
		}
	}
	fmt.Printf("准备就绪, 输入[run]以继续:")
	var WaiteEnter string
	_, _ = fmt.Scan(&WaiteEnter)
	if WaiteEnter != "run" {
		os.Exit(1)
	}

	var MessageHeader, MessageBody = BuildMessage(headers, formData)

	var Timer = new(BiliTimer).init(startTime, delayTime)
	Timer.WaitLocalTime(3)

	var client = H1CreateTlsConnection(headers["host"])
	H1SendMessage(client, MessageHeader)

	Timer.WaitSeverTime()
	var s = time.Now().UnixNano() / 1e6

	H1SendMessage(client, MessageBody)
	var res = H1ReceiveResponse(client, 1024)

	var e = time.Now().UnixNano() / 1e6

	_ = client.Close()

	fmt.Printf("%v\n", string(res))
	fmt.Printf("耗时%vms\n", e-s)
}
