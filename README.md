# BilibiliSuitBuy [b站装扮购买]

**B站装扮购买全模拟(98%)**

~~不是我说， [爬娘](https://space.bilibili.com/647193094)真的是，只有被人举办的才封，演起来没动的屁事没有~~

------------------------------------------------

<font size=4>**注：如果只是想试运行不要充足够的B币，现在b站是一步完成，下单即付款购买**</font>

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

这次舍弃了很多不必要的参数, 只需要填写```http_message_file```的值即可运行

~~[抓包教程(新)](https://www.bilibili.com/video/BV1Re411g7f5/)先看着，有时间找个新电脑录个~~

锁定url为 ```/x/garb/v2/mall/suit/detail``` 的包, 选中后点击 ```Raw```

```ctrl+a```全选```ctrl+c```复制, 然后创建一个文本文件```ctrl+v```粘贴进去 最后```ctrl+s```保存

```http_message_file```就写刚刚创建的文本文件路径

------------------------------------------------

<font size=4>**运行（python-socket）：**</font>

同python-requests

摸了先

------------------------------------------------
<font size=4>**运行（golang）：**</font>

摸了

------------------------------------------------
<font size=6>**总结：** </font>

你好，我是秦始皇，其实我并没有死，我在西安有100吨黄金，我现在需要2000元人民币解冻我在西安的黄金，你微信，支付宝转给我都可以。账号就是我的手机号码！转过来后，我明天直接带部队复活，让你统领三军！
