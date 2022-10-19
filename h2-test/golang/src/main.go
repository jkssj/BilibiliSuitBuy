package main

import (
	"crypto/tls"
	"fmt"
	"golang.org/x/net/http2/hpack"
	"golang/src/TH2"
)

func main() {
	//var Settings = TH2.NewSettingsFrames()
	//var body = TH2.BuildSettingsFrames(Settings)
	//var data = new(TH2.H2Connection)
	//data.InitiateConnection(nil)
	//fmt.Printf("%v\n", body)

	var TlsConfig *tls.Config = &tls.Config{
		NextProtos: []string{"h2"},
	}
	var con, _ = tls.Dial("tcp", "api.bilibili.com:443", TlsConfig)

	var h2 = new(TH2.H2Connection)
	h2.InitiateConnection(nil)
	var InitData = h2.DataToSend()

	fmt.Printf("InitData: %v\n", InitData)
	var _, _ = con.Write(InitData)

	var headers = []hpack.HeaderField{
		{Name: ":method", Value: "GET"},
		{Name: ":path", Value: "/x/space/acc/info?mid=1701735549"},
		{Name: ":authority", Value: "api.bilibili.com"},
		{Name: ":scheme", Value: "https"},
		{Name: "User-Agent", Value: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"},
	}
	h2.SendHeaders(1, headers, true)

	var HeaderData = h2.DataToSend()
	fmt.Printf("HeaderData: %v\n", HeaderData)
	_, _ = con.Write(HeaderData)

	//h2.SendData(1, []byte("headers"), true)
	//h2.DataToSend()
	for {
		var buf = make([]byte, 4096)

		var ReadLength, _ = con.Read(buf)

		//fmt.Printf("%v\n", buf[:ReadLength])

		//fmt.Printf("%v\n", buf)
		fmt.Printf("data: %v\n", buf[:ReadLength])

		var events = h2.ReceiveData(buf[:ReadLength])
		for _, event := range events {
			fmt.Printf("%v\n", event)
			if event.FrameType == 3 {
				goto EXIT
			}
			if event.FrameType == 0 {
				goto EXIT
			}
		}
		var data = h2.DataToSend()
		fmt.Printf("DataToSend: %v\n", data)
		_, _ = con.Write(data)
	}

EXIT:
	fmt.Printf("%v\n", "end")
}
