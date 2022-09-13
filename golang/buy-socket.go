package main

import (
	"bytes"
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"hash"
	"math"
	"math/rand"
	"net"
	"net/url"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

type Config struct {
	Host        string
	CouponToken string
	FSource     string
	ShopFrom    string

	SaleTime int64
	AddMonth int64
	BuyNum   int64
}

func GetRandomText(size int64) string {
	var KeyString string = "abcdef0123456789"
	var Buffer []byte = make([]byte, 0, size)
	var RandomBytes = bytes.NewBuffer(Buffer)
	rand.Seed(time.Now().UnixNano())
	for i := 0; i < int(size); i++ {
		RandInt := rand.Intn(len(KeyString))
		RandomBytes.WriteByte(KeyString[RandInt])
	}
	return RandomBytes.String()
}

func BiliTraceId(SaleTime string) string {
	var __SaleTime, _ = strconv.ParseFloat(SaleTime, 64)
	var RoundTime int64 = int64(math.Round(__SaleTime / 256))
	var back6 string = strconv.FormatInt(RoundTime, 16)
	var RandomText string = GetRandomText(32)
	var _data1 string = RandomText[6:] + back6
	var _data2 string = RandomText[22:] + back6
	return fmt.Sprintf("%v:%v:0:0", _data1, _data2)
}

func UrlEncode(FormData map[string]string) string {
	var ParamList []string
	for key, value := range FormData {
		var Key string = url.QueryEscape(key)
		var Value string = url.QueryEscape(value)
		var Param string = fmt.Sprintf("%v=%v", Key, Value)
		ParamList = append(ParamList, Param)
	}
	sort.Strings(ParamList)
	return strings.Join(ParamList, "&")
}

func AddFormDataSign(FormData string) string {
	var AppSec string = "560c52ccd288fed045859ed18bffd973"
	var FormDataSec string = fmt.Sprintf("%v%v", FormData, AppSec)
	var Md5Hash hash.Hash = md5.New()
	Md5Hash.Write([]byte(FormDataSec))
	var SignUint8 []uint8 = Md5Hash.Sum(nil)
	var FormDataSign string = hex.EncodeToString(SignUint8)
	return fmt.Sprintf("%v&sign=%v", FormData, FormDataSign)
}

func FileReader(filename string) string {
	var Message, _ = os.ReadFile(filename)
	return string(Message)
}

func CookieStrToMap(CookieText string) map[string]string {
	var CookieMap map[string]string = make(map[string]string)
	var CookieList []string = strings.Split(CookieText, "; ")
	for _, value := range CookieList {
		var TextList []string = strings.Split(value, "=")
		CookieMap[TextList[0]] = TextList[1]
	}
	return CookieMap
}

func ParseHttpMessage(HttpMessage string) map[string]string {
	var MessageList []string = strings.Split(HttpMessage, "\r\n")
	var MessageMap map[string]string = make(map[string]string)
	var ValueMap map[string]string = make(map[string]string)
	for _, value := range MessageList[1:] {
		var ValueList = strings.Split(value, ": ")
		if len(ValueList) == 2 {
			var key = strings.ToLower(ValueList[0])
			MessageMap[key] = ValueList[1]
		}
	}

	var HeaderMap map[string]string = make(map[string]string)
	var MessageHeader string = MessageList[0]
	var HeaderList []string = strings.Split(MessageHeader, " ")
	var MessageUrl string = HeaderList[1]
	var MessageUrlList []string = strings.Split(MessageUrl, "?")
	var Params string = MessageUrlList[1]
	var ParamsList []string = strings.Split(Params, "&")
	for _, value := range ParamsList {
		var ParamsValueList []string = strings.Split(value, "=")
		HeaderMap[ParamsValueList[0]] = ParamsValueList[1]
	}

	var statistics, _ = url.QueryUnescape(HeaderMap["statistics"])
	ValueMap["cookie"] = MessageMap["cookie"]
	ValueMap["access_key"] = HeaderMap["access_key"]
	ValueMap["appkey"] = HeaderMap["appkey"]
	ValueMap["item_id"] = HeaderMap["item_id"]
	ValueMap["statistics"] = statistics
	ValueMap["user-agent"] = MessageMap["user-agent"]
	ValueMap["aurora-eid"] = MessageMap["x-bili-aurora-eid"]
	return ValueMap
}

func UpdateHttpMessage(ValueMap map[string]string, config *Config) []byte {
	var __SaleTime string = strconv.FormatInt(config.SaleTime, 10)
	var __AddMonth string = strconv.FormatInt(config.AddMonth, 10)
	var __BuyNum string = strconv.FormatInt(config.BuyNum, 10)

	var __CouponToken string = config.CouponToken
	var __ShopFrom string = config.ShopFrom
	var __FSource string = config.FSource
	var __Host string = config.Host

	var __CookieText string = ValueMap["cookie"]
	var __UserAgent string = ValueMap["user-agent"]
	var __ItemId string = ValueMap["item_id"]
	var __AuroraEid string = ValueMap["aurora-eid"]
	var __statistics string = ValueMap["statistics"]
	var __AccessKey string = ValueMap["access_key"]
	var __AppKey string = ValueMap["appkey"]

	var __CookieMap map[string]string = CookieStrToMap(__CookieText)

	var __BiliJct string = __CookieMap["bili_jct"]
	var __DedeUserID string = __CookieMap["DedeUserID"]

	var __RefererParams = "?id=%v&navhide=1&f_source=%v&from=%v"
	var __Referer string = fmt.Sprintf(__RefererParams, __ItemId, __FSource, __ShopFrom)
	var __TraceId string = BiliTraceId(__SaleTime)

	var FormDataInit = UrlEncode(map[string]string{
		"access_key":   __AccessKey,
		"add_month":    __AddMonth,
		"appkey":       __AppKey,
		"buy_num":      __BuyNum,
		"coupon_token": __CouponToken,
		"csrf":         __BiliJct,
		"currency":     "bp",
		"disable_rcmd": "0",
		"f_source":     __FSource,
		"from":         __ShopFrom,
		"from_id":      "",
		"item_id":      __ItemId,
		"platform":     "android",
		"statistics":   __statistics,
		"ts":           __SaleTime,
	})

	var FormData string = AddFormDataSign(FormDataInit)
	var FormDataLength string = strconv.FormatInt(int64(len(FormData)), 10)

	var HttpMessage string
	HttpMessage += fmt.Sprintf("POST https://%v/x/garb/v2/trade/create HTTP/1.1\r\n", __Host)
	HttpMessage += fmt.Sprintf("native_api_from: h5\r\nCookie: %v\r\n", __CookieText)
	HttpMessage += "Accept: application/json, text/plain, */*\r\n"
	HttpMessage += fmt.Sprintf("Referer: https://www.bilibili.com/h5/mall/suit/detail%v\r\n", __Referer)
	HttpMessage += fmt.Sprintf("env: prod\r\nAPP-KEY: android\r\nUser-Agent: %v\r\n", __UserAgent)
	HttpMessage += fmt.Sprintf("x-bili-trace-id: %v\r\nx-bili-aurora-eid: %v\r\n", __TraceId, __AuroraEid)
	HttpMessage += fmt.Sprintf("x-bili-mid: %v\r\nx-bili-aurora-zone: \r\n", __DedeUserID)
	HttpMessage += "Content-Type: application/x-www-form-urlencoded; charset=utf-8\r\n"
	HttpMessage += fmt.Sprintf("Content-Length: %v\r\nHost: %v\r\n", FormDataLength, __Host)
	HttpMessage += fmt.Sprintf("Connection: Keep-Alive\r\nAccept-Encoding: gzip\r\n\r\n%v", FormData)

	return []byte(HttpMessage)
}

func main() {
	var config = new(Config)
	(*config).Host = "api.bilibili.com"
	(*config).FSource = "shop"
	(*config).CouponToken = ""
	(*config).ShopFrom = "feed.card"
	(*config).SaleTime = 1663058122
	(*config).BuyNum = 1
	(*config).AddMonth = -1

	var HttpMessageFile string = FileReader("message.txt")
	var MessageMap map[string]string = ParseHttpMessage(HttpMessageFile)
	var HttpMessage []byte = UpdateHttpMessage(MessageMap, config)

	var Adder = fmt.Sprintf("%v:80", (*config).Host)
	var client, _ = net.Dial("tcp", Adder)
	var result []uint8 = make([]byte, 4096)
	var StartTime int64 = time.Now().UnixNano() / 1e6
	var _, _ = client.Write(HttpMessage)
	var _, _ = client.Read(result)
	var EndTime int64 = time.Now().UnixNano() / 1e6

	fmt.Printf("%v\n", string(result))
	fmt.Printf("%v\n", EndTime-StartTime)

}
