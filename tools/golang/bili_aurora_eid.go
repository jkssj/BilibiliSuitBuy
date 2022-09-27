package main

import (
	"encoding/base64"
	"fmt"
)

func BiliAuroraEidGolang(mid string) string {
	var length int = len(mid)
	var barr []byte = make([]byte, length)
	if length-1 < 0 {
		return ""
	}
	for i := 0; i < length; i++ {
		var a uint8 = mid[i]
		var b uint8 = "ad1va46a7lza"[i%12]
		barr[i] = a ^ b
	}
	return base64.StdEncoding.EncodeToString(barr)
}

func main() {
	var eid string = BiliAuroraEidGolang("1701735549")
	fmt.Printf("%v", eid)
}
