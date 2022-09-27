package main

import (
	"fmt"
	"net/url"
	"os"
	"strings"
)

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

func ParseHttpMessage(HttpMessage string) map[string]any {
	var MessageList []string = strings.Split(HttpMessage, "\r\n")
	var MessageMap map[string]string = make(map[string]string)
	var ValueMap map[string]any = make(map[string]any)
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

	var CookieText string = MessageMap["cookie"]
	var statistics, _ = url.QueryUnescape(HeaderMap["statistics"])
	var CookieMap map[string]string = CookieStrToMap(CookieText)
	ValueMap["cookie"] = CookieText
	ValueMap["cookie_map"] = CookieMap
	ValueMap["access_key"] = HeaderMap["access_key"]
	ValueMap["appkey"] = HeaderMap["appkey"]
	ValueMap["item_id"] = HeaderMap["item_id"]
	ValueMap["statistics"] = statistics
	ValueMap["user-agent"] = MessageMap["user-agent"]
	ValueMap["x-bili-aurora-eid"] = MessageMap["x-bili-aurora-eid"]
	return ValueMap
}

func main() {
	var HttpMessage string = FileReader("C:\\Users\\afue\\Desktop\\bili-suit-buy\\socket-test\\message.txt")
	var MessageMap map[string]any = ParseHttpMessage(HttpMessage)
	fmt.Printf("%v", MessageMap)
	for key, value := range MessageMap {
		fmt.Printf("key:%v valeu:%v\n", key, value)
	}
}
