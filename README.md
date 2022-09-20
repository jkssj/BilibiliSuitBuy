# BilibiliSuitBuy [b站装扮购买]

**B站装扮购买全模拟(98%)**

------------------------------------------------

<font size=4>**此装扮购买脚本后续更新的代码均不包含计时器**</font>

<font size=2>**使用GoLang, Python两个语言分别编写2个逻辑相同的版本**</font>

<font size=2>**python-requests（弃了）： 采用requests库来请求，提前创建表单计算sign啥的远古版本就有了**</font>

<font size=2>**python-socket： 采用socket提前连接，包含提前创建表单，计算sign等**</font>

<font size=2>**golang-socket：和python思路一样，socket提前链接，提前创建表单和计算sign**</font>

<font size=1>**注：如果只是想试运行不要充足够的B币，现在b站是一步完成，下单即付款购买**</font>

------------------------------------------------

<font size=4>**运行（python-requests）：**</font>

安装 ```requests``` ``` pip install requests ```

```

# ./python/buy-requests.py

def main():
    suit_buy = SuitBuy(
        http_message_file="./message/message.txt",

        # 可选
        add_month="-1",
        buy_num="1",
        coupon_token="",
        host="api.bilibili.com",
        f_source="shop",
        shop_from="feed.card",
        sale_time=round(time.time())
    )

    # suit_buy.test()
    print(suit_buy.start().text)


if __name__ == '__main__':
    main()
```

不急一个一个看

| key               | value       | default          |
|-------------------|-------------|------------------|
| http_message_file | fiddler报文路径 | None             |
| add_month         | 购买时长        | -1               |
| buy_num           | 购买数量        | 1                |
| host              | 地址          | api.bilibili.com |
| f_source          | 购买源头        | shop             |
| shop_from         | 进入源头        | feed.card        |
| sale_time         | 购买/开售 时间    | 当前时间             |
| coupon_token      | 优惠卷         | None             |

这次舍弃了很多不必要的参数, 只需要填写```http_message_file```的值即可运行

~~[抓包教程(新)](https://www.bilibili.com/video/BV1Re411g7f5/)先看着，有时间找个新电脑录个~~

锁定url为 ```/x/garb/v2/mall/suit/detail``` 的包, 选中后点击 ```Raw```

```ctrl+a```全选```ctrl+c```复制, 然后创建一个文本文件```ctrl+v```粘贴进去 最后```ctrl+s```保存

```http_message_file```就写刚刚创建的文本文件路径

------------------------------------------------

<font size=4>**运行（python-socket）：**</font>

同python-requests

众所周知服务端接收不到客户端的body会阻塞，尝试报文取最后一个字节，其他的提前发送，再接收1bit的数据来判断服务器处理完成

这样就变成了到时间 发送1bit大小数据，再接收1bit大小的数据来验证服务器处理，来回时间明显下降

快过requests，略微快过socket提前连接直接发送全部报文

------------------------------------------------
<font size=4>**运行（golang-socket）：**</font>

无需安装任何第三方库（我不想用那包管理器，太恶心了，可能因为用惯pip了）

```
func main() {
	var config = new(Config)
	(*config).Host = "api.bilibili.com"
	(*config).FSource = "shop"
	(*config).CouponToken = ""
	(*config).ShopFrom = "feed.card"
	(*config).SaleTime = time.Now().Unix()
	(*config).BuyNum = 1
	(*config).AddMonth = -1
	var FileSavePath string = "./message.txt"
	var HttpMessageFile string = FileReader(FileSavePath)
	...
}
```

| key                   | value       | default           |
|-----------------------|-------------|-------------------|
| FileSavePath          | fiddler报文路径 | None              |
| (*config).AddMonth    | 购买时长        | -1                |
| (*config).BuyNum      | 购买数量        | 1                 |
| (*config).Host        | 地址          | api.bilibili.com  |
| (*config).FSource     | 购买源头        | shop              |
| (*config).ShopFrom    | 进入源头        | feed.card         |
| (*config).SaleTime    | 购买/开售 时间    | time.Now().Unix() |
| (*config).CouponToken | 优惠卷         | None              |

~~[抓包教程(新)](https://www.bilibili.com/video/BV1Re411g7f5/)先看着，有时间找个新电脑录个~~

锁定url为 ```/x/garb/v2/mall/suit/detail``` 的包, 选中后点击 ```Raw```

```ctrl+a```全选```ctrl+c```复制, 然后创建一个文本文件```ctrl+v```粘贴进去 最后```ctrl+s```保存

```FileSavePath```就写刚刚创建的文本文件路径（最好就绝对路径）

------------------------------------------------
<font size=6>**总结：** </font>

~~不是我说， [爬娘](https://space.bilibili.com/647193094)真的是，只有被人举办的才封，演起来没动的屁事没有~~

你好，我是秦始皇，其实我并没有死，我在西安有100吨黄金，我现在需要2000元人民币解冻我在西安的黄金，你微信，支付宝转给我都可以。账号就是我的手机号码！转过来后，我明天直接带部队复活，让你统领三军！
