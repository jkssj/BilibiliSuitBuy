# BilibiliSuitBuy [b站装扮购买]

**B站装扮购买模拟（98%）**

------------------------------------------------

**特点：**

**提前开始数据交换**

**网络正常几乎不会出现100ms以上的情况**

------------------------------------------------

- [x] **qr code login**
- [x] **access_key**
- [x] **cookies**
- [x] **x-bili-aurora-eid**
- [x] **x-bili-trace-id**
- [x] **HTTP1.1**
- [x] **HTTP2.0**

------------------------------------------------

<font size=4>**运行buy-requests.py：**</font>

~~弃了，太慢了，虽然还是比绿色用户快就是~~

------------------------------------------------

<font size=4>**运行 buy-socket-http1.py ：**</font>

```

# /suit_buy/python/buy-socket-http1.py

def main():
    sale_time = 1665889008  # 开售时间

    suit_buy = SuitBuy(
        http_message=open(r"../http-message/HTTP1.1Message.txt", "rb").read(),
        sale_time=sale_time,

        # 可选
        add_month="-1",
        buy_num="1",
        coupon_token="",
        host="api.bilibili.com",
        f_source="shop",
        shop_from="feed.card",
    )

    # 跳出本地计时器后
    client = suit_buy.CreateTlsConnection()
    suit_buy.SendMessageHeader(client)

    # 等待服务器计时退出
    suit_buy.SendMessageBody(client)
    response = suit_buy.ReceiveResponse(client)

    print(response.decode())

    # 关闭连接
    client.close()


if __name__ == '__main__':
    main()
```

| key          | value       | default          |
|--------------|-------------|------------------|
| http_message | http1.1报文数据 | 必要/None          |
| sale_time    | 购买/开售 时间    | 必要/None          |
| add_month    | 购买时长        | -1               |
| buy_num      | 购买数量        | 1                |
| host         | 地址          | api.bilibili.com |
| f_source     | 购买源头        | shop             |
| shop_from    | 进入源头        | feed.card        |
| coupon_token | 优惠卷         | None             |

------------------------------------------------

<font size=4>**运行 buy-socket-http1.py ：**</font>

**需要安装 [python-hyper/h2](https://github.com/python-hyper/h2)**

```

# /suit_buy/python/buy-socket-http2.py

def main():
    sale_time = 1665901776

    suit_buy = SuitBuy(
        http_message=open(r"../http-message/HTTP2.0Message.txt", "rb").read(),
        sale_time=sale_time,

        # 可选
        add_month="-1",
        buy_num="1",
        coupon_token="",
        host="api.bilibili.com",
        f_source="shop",
        shop_from="feed.card",
    )

    # 跳出本地计时器后
    client = suit_buy.CreateTlsConnection()
    suit_buy.SendMessageHeader(client)

    # 等待服务器计时退出
    suit_buy.SendMessageBody(client)
    response = suit_buy.ReceiveResponse(client)

    print(response.decode())

    # 关闭连接
    suit_buy.ClientClose(client)


if __name__ == '__main__':
    main()
```

| key          | value       | default          |
|--------------|-------------|------------------|
| http_message | http2.0报文数据 | 必要/None          |
| sale_time    | 购买/开售 时间    | 必要/None          |
| add_month    | 购买时长        | -1               |
| buy_num      | 购买数量        | 1                |
| host         | 地址          | api.bilibili.com |
| f_source     | 购买源头        | shop             |
| shop_from    | 进入源头        | feed.card        |
| coupon_token | 优惠卷         | None             |

------------------------------------------------

<font size=4>**运行 buy-socket-http1.go ：**</font>

```
func main() {
	// Config都是必要
	// 一般只要改saleTim就行
	var saleTime = 1666427455
	var filePath = "./buy_suit/http-message/HTTP1.1Message.txt"
	var config = new(Config)
	(*config).saleTime = int64(saleTime)
	(*config).host = "api.bilibili.com"
	(*config).shopFrom = "feed.card"
	(*config).fSource = "shop"
	(*config).buyNum = 1
	(*config).addMonth = -1
	(*config).couponToken = ""

	var header, body = BuildAll(filePath, config)
	//fmt.Printf("%v\n", string(header))
	//fmt.Printf("%v\n", string(body))

	// 跳出本地计时器
	var client = CreateTlsConnection(config)

	var s = time.Now().UnixNano() / 1e6

	SendMessage(client, header) // 发送n-1的内容

	// 跳出服务器计时器
	SendMessage(client, body)              // 发送剩余的内容
	var response = ReceiveResponse(client) // 接收响应

	var e = time.Now().UnixNano() / 1e6

	fmt.Printf("%v\n", string(response))
	fmt.Printf("耗时:%vs\n", e-s)
}
```

------------------------------------------------

**抓包教程：**

~~[抓包教程(新)](https://www.bilibili.com/video/BV1Re411g7f5/)先看着，有时间找个新电脑录个~~

锁定url为 ```/x/garb/v2/mall/suit/detail``` 的包, 选中后点击 ```Raw```

```ctrl+a```全选```ctrl+c```复制, 然后创建一个文本文件```ctrl+v```粘贴进去 最后```ctrl+s```保存

保存的文件就是http报文的文件, Fiddler Everywhere需要开启HTTP2才能抓HTTP2, Classic只有HTTP1.1

------------------------------------------------

**参考：**

[github.com/python-hyper/h2](https://github.com/python-hyper/h2)

[plain-sockets-example.html](https://python-hyper.org/projects/h2/en/stable/plain-sockets-example.html)

------------------------------------------------

<details>

<summary>V我😋</summary>

公开的都还有人找定制，停更了

<div align=center><img src="./reward.gif"></div>

</details>

------------------------------------------------

你问我为什么不开，我没钱，我没账号，我没设备，我没渠道，我啥都没有，我开个✓8

~~不是我说， [爬娘](https://space.bilibili.com/647193094)真的是，只有被人举办的才封，演起来没动的屁事没有~~
