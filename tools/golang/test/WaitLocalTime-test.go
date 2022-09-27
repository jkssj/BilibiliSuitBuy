package main

import (
	"fmt"
	"time"
)

func WaitLocalTime(SaleTime int64, jump int64) {
	var NowTime, JumpTime float64
	NowTime = float64(time.Now().UnixNano()) / 1e9
	JumpTime = float64(SaleTime - jump)
	for JumpTime >= NowTime {
		NowTime = float64(time.Now().UnixNano()) / 1e9
		fmt.Printf("\r%f", JumpTime-NowTime)
	}

}

func main() {
	var sale int64 = time.Now().UnixNano() / 1e9
	WaitLocalTime(sale+10, 3)
}
