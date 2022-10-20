package main

import (
	"bytes"
	"crypto/tls"
	"fmt"
	"golang/src/PH2"
)

func main() {
	var TlsConfig *tls.Config = &tls.Config{
		NextProtos: []string{"h2"},
	}

	var con, _ = tls.Dial("tcp", "httpbin.org:443", TlsConfig)

	var th2 = new(PH2.H2Connection)

	th2.InitiateConnection()
	th2.SendSettings(0, nil, 0)
	var SettingsData = th2.DataToSend()
	_, _ = con.Write(SettingsData)

	// POST
	//var headers = []hpack.HeaderField{
	//	{Name: ":method", Value: "POST"},
	//	{Name: ":path", Value: "/post"},
	//	{Name: ":authority", Value: "httpbin.org"},
	//	{Name: ":scheme", Value: "https"},
	//	{Name: "user-agent", Value: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"},
	//}
	//
	//th2.SendHeaders(1, headers, 4)
	//th2.SendData(1, []byte("next"), 1)

	// GET
	//var headers = []hpack.HeaderField{
	//	{Name: ":method", Value: "GET"},
	//	{Name: ":path", Value: "/get"},
	//	{Name: ":authority", Value: "httpbin.org"},
	//	{Name: ":scheme", Value: "https"},
	//	{Name: "user-agent", Value: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"},
	//}
	//th2.SendHeaders(1, headers, 5)

	var HeadersData = th2.DataToSend()
	_, _ = con.Write(HeadersData)

	var data []byte
	for {
		var buf = make([]byte, 8196)
		var length, _ = con.Read(buf)

		var events = th2.ReceiveData(buf[:length])
		for _, event := range events {
			
			//fmt.Printf("%v\n", event)
			
			if value, ok := event.(*PH2.DataFrame); ok == true {
				fmt.Printf("%v\n", value.Flags)
				if value.Flags == 1 {
					goto EXIT
				}
				data = bytes.Join([][]byte{data, value.Body}, []byte(""))
			}
		}
	}
EXIT:
	fmt.Printf("%v\n", string(data))

}
