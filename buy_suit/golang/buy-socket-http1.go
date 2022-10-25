package main

import (
	"bytes"
	"crypto/md5"
	"crypto/tls"
	"encoding/hex"
	"fmt"
	"math/rand"
	"net/url"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

type Config struct {
	saleTime    int64
	addMonth    int64
	buyNum      int64
	host        string
	couponToken string
	fSource     string
	shopFrom    string
}

// buildRandomText
// 生成一个随机字符串, 代替原uuid4
func buildRandomText(size int64) string {
	var KeyString = "abcdef0123456789"
	var RandomBytes bytes.Buffer
	rand.Seed(time.Now().UnixNano())
	for i := 0; i < int(size); i++ {
		RandInt := rand.Intn(len(KeyString))
		RandomBytes.WriteByte(KeyString[RandInt])
	}
	return RandomBytes.String()
}

// urlEncode
// 表单转url编码
func urlEncode(FormData map[string]string) string {
	var ParamList []string
	for key, value := range FormData {
		var Key = url.QueryEscape(key)
		var Value = url.QueryEscape(value)
		var param = fmt.Sprintf("%v=%v", Key, Value)
		ParamList = append(ParamList, param)
	}
	sort.Strings(ParamList)
	return strings.Join(ParamList, "&")
}

// ------------------------------------------------------------------------

// BiliTraceId
// 生成TraceId
func BiliTraceId(Time int64) string {
	var back6 = strconv.FormatInt(Time, 16)
	var RandomText = buildRandomText(32)
	var a, b = RandomText[6:] + back6, RandomText[22:] + back6
	return fmt.Sprintf("%v:%v:0:0", a, b)
}

// AddFormDataSign
// 为表单添加sign
func AddFormDataSign(FormData string) string {
	var AppSec = "560c52ccd288fed045859ed18bffd973"
	var FormDataSec = fmt.Sprintf("%v%v", FormData, AppSec)
	var Md5Hash = md5.New()
	Md5Hash.Write([]byte(FormDataSec))
	var SignUint8 = Md5Hash.Sum(nil)
	var FormDataSign = hex.EncodeToString(SignUint8)
	return fmt.Sprintf("%v&sign=%v", FormData, FormDataSign)
}

// parseHttpMessage
// 解析http1.1报文数据
func parseHttpMessage(content []byte) (map[string]string, map[string]string) {
	var MessageList = strings.Split(string(content), "\r\n")

	var MessageMap = make(map[string]string)
	for _, value := range MessageList[1 : len(MessageList)-2] {
		var ValueList = strings.Split(value, ": ")
		if len(ValueList) != 2 {
			ValueList = []string{ValueList[0], ""}
		}
		var key = strings.ToLower(ValueList[0])
		MessageMap[key] = ValueList[1]
	}

	var ValueMap = make(map[string]string)
	var Url = strings.Split(MessageList[0], " ")[1]
	var Params = strings.Split(Url, "?")[1]
	var ParamsList = strings.Split(Params, "&")
	for _, value := range ParamsList {
		var ValueList = strings.Split(value, "=")
		if len(ValueList) != 2 {
			ValueList = []string{ValueList[0], ""}
		}
		var key, _ = url.QueryUnescape(ValueList[0])
		var _value, _ = url.QueryUnescape(ValueList[1])
		ValueMap[key] = _value
	}

	return MessageMap, ValueMap
}

// BuildFormData
// 生成表单
func BuildFormData(params map[string]string, config *Config) string {
	var FormData = map[string]string{
		"access_key":   params["access_key"],
		"add_month":    strconv.FormatInt((*config).addMonth, 10),
		"appkey":       params["appkey"],
		"buy_num":      strconv.FormatInt((*config).buyNum, 10),
		"coupon_token": (*config).couponToken,
		"csrf":         params["csrf"],
		"currency":     "bp",
		"disable_rcmd": "0",
		"f_source":     (*config).fSource,
		"from":         (*config).shopFrom,
		"from_id":      "",
		"item_id":      params["item_id"],
		"m_source":     "",
		"platform":     "android",
		"statistics":   params["statistics"],
		"ts":           strconv.FormatInt((*config).saleTime, 10),
	}
	return AddFormDataSign(urlEncode(FormData))
}

// BuildMessage
// 生成报文
func BuildMessage(config *Config, headers map[string]string, formData string) []byte {
	var message = "POST /x/garb/v2/trade/create HTTP/1.1\r\n"
	message += fmt.Sprintf("native_api_from: %v\r\n", headers["native_api_from"])
	message += fmt.Sprintf("Cookie: %v\r\n", headers["cookie"])
	message += fmt.Sprintf("Accept: %v\r\n", headers["accept"])
	message += fmt.Sprintf("Referer: %v\r\n", headers["referer"])
	message += fmt.Sprintf("env: %v\r\n", headers["env"])
	message += fmt.Sprintf("APP-KEY: %v\r\n", headers["app-key"])
	message += fmt.Sprintf("User-Agent: %v\r\n", headers["user-agent"])
	message += fmt.Sprintf("x-bili-trace-id: %v\r\n", BiliTraceId((*config).saleTime))
	message += fmt.Sprintf("x-bili-aurora-eid: %v\r\n", headers["x-bili-aurora-eid"])
	message += fmt.Sprintf("x-bili-mi: %v\r\n", headers["x-bili-mid"])
	message += fmt.Sprintf("x-bili-aurora-zone: %v\r\n", headers["x-bili-aurora-zone"])
	message += "Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n"
	message += fmt.Sprintf("Content-Length: %v\r\n", len(formData))
	message += fmt.Sprintf("Host: %v\r\n", config.host)
	message += fmt.Sprintf("Connection: %v\r\n", headers["connection"])
	message += fmt.Sprintf("Accept-Encoding: %v\r\n\r\n", headers["accept-encoding"])
	return []byte(message + formData)
}

// BuildAll
// 生成所有
func BuildAll(filePath string, config *Config) ([]byte, []byte) {
	var Message, _ = os.ReadFile(filePath)
	var MessageMap, ValueMap = parseHttpMessage(Message)
	var FormData = BuildFormData(ValueMap, config)
	var HttpMessage = BuildMessage(config, MessageMap, FormData)
	return HttpMessage[:len(HttpMessage)-1], HttpMessage[len(HttpMessage)-1:]
}

// CreateTlsConnection
// 创建连接
func CreateTlsConnection(config *Config) *tls.Conn {
	var TlsConfig *tls.Config = &tls.Config{
		InsecureSkipVerify: false,
		ServerName:         config.host,
		MinVersion:         tls.VersionTLS12,
		MaxVersion:         tls.VersionTLS12,
		ClientAuth:         tls.RequireAndVerifyClientCert,
	}
	var adder = fmt.Sprintf("%v:443", config.host)
	var client, err = tls.Dial("tcp", adder, TlsConfig)
	if err != nil {
		fmt.Printf("%v\n", err)
		os.Exit(1)
	}
	return client
}

// SendMessage
// 发送请求
func SendMessage(client *tls.Conn, body []byte) {
	_, _ = client.Write(body)
}

// ReceiveResponse
// 接收响应
func ReceiveResponse(client *tls.Conn) []byte {
	var result = make([]byte, 8192)
	var length, _ = client.Read(result)
	return result[:length]
}

func main() {

	// Config都是必要
	// 一般只要改saleTim就行
	var saleTime = 1666427455
	var filePath = "./buy_suit/http-message/HTTP1.1Message.txt"
	var config = new(Config)
	(*config).saleTime = int64(saleTime)
	(*config).host = "api.bilibili.com"
	(*config).shopFrom = "feed.card"
	(*config).fSource = "shop"
	(*config).buyNum = 1
	(*config).addMonth = -1
	(*config).couponToken = ""

	var header, body = BuildAll(filePath, config)
	//fmt.Printf("%v\n", string(header))
	//fmt.Printf("%v\n", string(body))

	// 跳出本地计时器
	var client = CreateTlsConnection(config)

	var s = time.Now().UnixNano() / 1e6

	SendMessage(client, header) // 发送n-1的内容

	// 跳出服务器计时器
	SendMessage(client, body)              // 发送剩余的内容
	var response = ReceiveResponse(client) // 接收响应

	var e = time.Now().UnixNano() / 1e6

	fmt.Printf("%v\n", string(response))
	fmt.Printf("耗时:%vs\n", e-s)
}
