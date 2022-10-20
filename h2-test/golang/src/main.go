package main

import (
	"crypto/tls"
	"fmt"
	"golang.org/x/net/http2/hpack"
	"hh2/src/TH2"
)

func main() {

	var TlsConfig *tls.Config = &tls.Config{
		NextProtos: []string{"h2"},
	}

	var con, _ = tls.Dial("tcp", "api.bilibili.com:443", TlsConfig)

	var th2 = new(TH2.H2Connection)

	th2.InitiateConnection()
	//var InitData = th2.DataToSend()
	//_, _ = con.Write(InitData)
	//fmt.Printf("%v\n", InitData)

	th2.SendSettings(nil)
	var SettingsData = th2.DataToSend()
	_, _ = con.Write(SettingsData)
	fmt.Printf("%v\n", SettingsData)

	var headers = []hpack.HeaderField{
		{Name: ":method", Value: "GET"},
		{Name: ":path", Value: "/x/space/acc/info?mid=1701735549"},
		{Name: ":authority", Value: "api.bilibili.com"},
		{Name: ":scheme", Value: "https"},
		//{Name: "User-Agent", Value: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"},
	}

	th2.SendHeaders(1, headers, 5)
	var HeadersData = th2.DataToSend()
	_, _ = con.Write(HeadersData)

	fmt.Printf("%v\n", HeadersData)

	for i := 0; i < 4; i++ {
		var buf = make([]byte, 4096)
		var length, _ = con.Read(buf)
		var data = buf[:length]
		fmt.Printf("data:%v\n", data)
		if i == 0 {
			_, _ = con.Write([]byte{0, 0, 0, 4, 1, 0, 0, 0, 0})
		}
	}
}
