# BilibiliSuitBuy [b站装扮购买]

**B站装扮购买模拟（98%）**

h2的暂时不能用，我找找原因

------------------------------------------------

**特点：**

**提前生成所有要使用的数据（sign...）**

**你可以使用socket来提前进行和服务器的数据交换**

**而不是等待倒计时结束才开始创建一个连接，然后开始数据交换**

**分割报文，分成 n-1:1**

**提前进行连接,提前发送n-1大小的报文（服务器回阻塞，所以可以留1bit数据等到时间发送）**

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

<font size=4>**运行 buy-socket.go ：**</font>

```
func main() {
	var FilePath string = "./buy_suit/http-message/HTTP1.1Message.txt" // 报文文件路径
	var SaleTime = time.Now().Unix()                                   // 装扮开售时间

	var config *Config = &DefaultConfig
	(*config).Host = "api.bilibili.com"
	(*config).ShopFrom = "feed.card"
	(*config).FSource = "shop"
	(*config).BuyNum = 1
	(*config).AddMonth = -1
	(*config).CouponToken = ""

	var SuitBuyC *SuitBuy = new(SuitBuy).init(FilePath, SaleTime, config)

	// 跳出本地计时器

	SuitBuyC.LinkSever()  // 连接到服务器
	SuitBuyC.SendHeader() // 发送n-1的头数据

	// 跳出服务器计时器

	SuitBuyC.SendBody() // 发出剩下的数据

	// 打印响应
	var Response string = SuitBuyC.ReceiveResponse()
	fmt.Printf("%v", Response)
}
```

| key                   | value       | default           |
|-----------------------|-------------|-------------------|
| FilePath              | fiddler报文路径 | None              |
| SaleTime              | 购买/开售 时间    | time.Now().Unix() |
| (*config).AddMonth    | 购买时长        | -1                |
| (*config).BuyNum      | 购买数量        | 1                 |
| (*config).Host        | 地址          | api.bilibili.com  |
| (*config).FSource     | 购买源头        | shop              |
| (*config).ShopFrom    | 进入源头        | feed.card         |
| (*config).CouponToken | 优惠卷         | None              |

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

**总结：**

**python-sokcet-buy-http1.1 2022/09/08-now **

**python-sokcet-buy-http2.0 2022/10/15-now **

**python-requests-buy 2022/01/13-now **

你先百度百度http1.x到http2都是基于什么的再说哪个脚本快啥的，这根本就不是一个类型

你问我为什么不开，我没钱，我没账号，我没设备，我没渠道，我啥都没有，我开个✓8

~~不是我说， [爬娘](https://space.bilibili.com/647193094)真的是，只有被人举办的才封，演起来没动的屁事没有~~

~~？你先开的~~

~~多线程 / 异步是错误的~~
