package main

import (
	"bytes"
	"crypto/md5"
	"crypto/tls"
	"encoding/hex"
	"fmt"
	"hash"
	"math"
	"math/rand"
	"net/url"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	DefaultCouponToken string = ""
	DefaultShopFrom    string = "feed.card"
	DefaultFSource     string = "shop"
	DefaultHost        string = "api.bilibili.com"

	DefaultAddMonth int64 = -1
	DefaultBuyNum   int64 = 1
)

type Config struct {
	Host        string
	CouponToken string
	FSource     string
	ShopFrom    string

	AddMonth int64
	BuyNum   int64
}

var DefaultConfig Config = Config{
	Host:        DefaultHost,
	CouponToken: DefaultCouponToken,
	FSource:     DefaultFSource,
	ShopFrom:    DefaultShopFrom,

	AddMonth: DefaultAddMonth,
	BuyNum:   DefaultBuyNum,
}

type SuitBuy struct {
	BuyMessageHeader []byte
	BuyMessageBody   []byte

	client *tls.Conn

	SaleTime float64
	Host     string
}

func ExitError(err error) {
	if err != nil {
		fmt.Printf("%v\n", err)
		os.Exit(1)
	}
}

func ReaderHttpMessageFile(FilePath string) string {
	var Message, err = os.ReadFile(FilePath)
	ExitError(err)
	return string(Message)
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

func UpdateHttpMessage(HttpMap map[string]string, SaleTime int64, config *Config) []byte {
	var __SaleTime string = strconv.FormatInt(SaleTime, 10)
	var __AddMonth string = strconv.FormatInt(config.AddMonth, 10)
	var __BuyNum string = strconv.FormatInt(config.BuyNum, 10)

	var __CouponToken string = config.CouponToken
	var __ShopFrom string = config.ShopFrom
	var __FSource string = config.FSource
	var __Host string = config.Host

	var __CookieText string = HttpMap["cookie"]
	var __UserAgent string = HttpMap["user-agent"]
	var __ItemId string = HttpMap["item_id"]
	var __AuroraEid string = HttpMap["aurora-eid"]
	var __statistics string = HttpMap["statistics"]
	var __AccessKey string = HttpMap["access_key"]
	var __AppKey string = HttpMap["appkey"]

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

func (bili *SuitBuy) init(FilePath string, SaleTime int64, config *Config) *SuitBuy {
	var HttpMessageContent string = ReaderHttpMessageFile(FilePath)
	var HttpMap map[string]string = ParseHttpMessage(HttpMessageContent)
	var BuyMessage []byte = UpdateHttpMessage(HttpMap, SaleTime, config)

	bili.BuyMessageHeader = BuyMessage[:len(BuyMessage)-1]
	bili.BuyMessageBody = BuyMessage[len(BuyMessage)-1:]
	bili.SaleTime = float64(SaleTime)
	bili.Host = config.Host
	return bili
}

func (bili *SuitBuy) LinkSever() {
	var Adder string = fmt.Sprintf("%v:443", bili.Host)
	var client, err = tls.Dial("tcp", Adder, nil)
	ExitError(err)
	bili.client = client
}

func (bili *SuitBuy) SendHeader() {
	var _, err = bili.client.Write(bili.BuyMessageHeader)
	ExitError(err)
}

func (bili *SuitBuy) SendBody() {
	var _, err = bili.client.Write(bili.BuyMessageBody)
	ExitError(err)
}

func (bili *SuitBuy) ReceiveResponse() string {
	var result []uint8 = make([]byte, 4096)
	var _, err = bili.client.Read(result)
	ExitError(err)
	var CloseErr = bili.client.Close()
	ExitError(CloseErr)
	return string(result)
}

func main() {
	var FilePath = "C:\\Users\\afue\\Desktop\\BilibiliSuitBuy-main\\buy_suit\\http-message\\HTTP1.1Message.txt"

	var config *Config = &DefaultConfig

	var SuitBuyC *SuitBuy = new(SuitBuy).init(FilePath, 1661675845, config)

	// 跳出本地计时器

	SuitBuyC.LinkSever()
	SuitBuyC.SendHeader()

	// 跳出服务器计时器

	SuitBuyC.SendBody() // 发出以后的数据

	// 打印响应
	var Response string = SuitBuyC.ReceiveResponse()
	fmt.Printf("%v", Response)
}
