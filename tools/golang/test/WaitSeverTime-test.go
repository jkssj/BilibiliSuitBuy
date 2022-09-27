package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

func GetSeverTime(client *http.Client, req *http.Request) float64 {
	var response, _ = client.Do(req)
	var data_, _ = io.ReadAll(response.Body)
	var JsonData = make(map[string]map[string]int64)
	var _ = json.Unmarshal(data_, &JsonData)
	var _ = response.Body.Close()
	return float64(JsonData["data"]["now"])
}

func main() {
	var client *http.Client = &http.Client{}
	var req, _ = http.NewRequest("GET", "https://api.bilibili.com/x/report/click/now", nil)
	var UserAgent string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"
	req.Header.Set("User-Agent", UserAgent)
	for li := range [10]int64{} {
		var NowTime = GetSeverTime(client, req)
		fmt.Printf("%v|%f|\n", li, NowTime)
		time.Sleep(1 * time.Second)
	}
}
