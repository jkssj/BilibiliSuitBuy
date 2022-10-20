package main

import (
	"bytes"
	"crypto/tls"
	"fmt"
	"golang.org/x/net/http2/hpack"
	"golang/src/TH2"
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
	//fmt.Printf("%v\n", SettingsData)

	var headers = []hpack.HeaderField{
		{Name: ":method", Value: "GET"},
		{Name: ":path", Value: "/x/space/acc/info?mid=1701735549"},
		{Name: ":authority", Value: "api.bilibili.com"},
		{Name: ":scheme", Value: "https"},
		{Name: "user-agent", Value: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"},
	}

	th2.SendHeaders(1, headers, 5)
	var HeadersData = th2.DataToSend()
	_, _ = con.Write(HeadersData)

	var data []byte

	for {
		var buf = make([]byte, 8196)
		var length, _ = con.Read(buf)
		fmt.Printf("%v\n", len(buf[:length]))

		var events = th2.ReceiveData(buf[:length])
		for _, event := range events {
			if value, ok := event.(*TH2.DataFrame); ok == true {
				//fmt.Printf("%v\n", len(value.Body))
				fmt.Printf("%v\n", "data")
				data = bytes.Join([][]byte{data, value.Body}, []byte(""))
				goto EXIT
			}
		}
	}
EXIT:
	fmt.Printf("%v\n", string(data))
}
