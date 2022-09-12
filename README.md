# BilibiliSuitBuy [b站装扮购买]

**B站装扮购买全模拟(98%)**

socket直接发报文已更新

别急，等我把golang的摸出来再慢慢写markdown

呃你那这个事啊我们讲不是说不是说不办那么但是呢没有说啊没有任何一件事情我们谈说说一定怎么怎么样说不行吗他也不是我们讲事在人为啊我们可以办法啊可以想办法，你这样晚一点晚一点咱们到时候呢，对吧我这个对吧这个包括哎呀我这个到时候你看一看是吧完了呢我把你这个事对吧好吧啊兄弟。

~~不是我说， [爬娘](https://space.bilibili.com/647193094)真的是，只有被人举办的才封，演起来没动的屁事没有~~



------------------------------------------------

<font size=4>**注：如果只是想试运行不要充足够的B币，现在一步完成，下单即付款购买**</font>

------------------------------------------------

<font size=4>**运行：**</font>

安装 ```requests``` ``` pip install requests ```

```
from test_value import cookie_test, access_key_test, bili_eid_test

suit = SuitBuy(
    # 代理设置
    # trust_env=False,
    # proxies={"http": None, "https": None},

    # 装扮设置
    shop_from="feed.card",
    coupon_token="",
    f_source="shop",
    add_month="-1",
    item_id="37825",
    buy_num="1",
    sale_time=round(time.time()),
    app_key="1d8b6e7d45233436",

    # 访问头设置(外)
    # header_app_key=DefaultHeaderAPPKEY,
    # accept_encoding=DefaultAcceptEncoding,
    # content_type=DefaultContentType,
    # connection=DefaultConnection,
    # api_from=DefaultApiFrom,
    # accept=DefaultAccept,
    # host=DefaultHost,
    # env=DefaultEnv,

    # 访问头设置(UserAgent)
    system_version="9",
    channel="yingyongbao",
    sdk_int="28",
    version="6.87.0",
    session="1a7fb931",
    buv_id="XY30A9D303849C51D0D6F863F84A269E887E8",
    phone="M2007J22C",
    build="6870300",

    # 用户验证
    access_key=access_key_test,
    bili_eid=bili_eid_test,
    cookie=cookie_test
)
suit.PrintValue()
# print(suit.run().text)
```

不急一个一个看

| key            | value        |
|----------------|--------------|
| shop_from      | 详情页来源        |
| coupon_token   | 优惠卷token     |
| f_source       | 装扮购买位置       |
| add_month      | 购买时长         |
| item_id        | 装扮标识         |
| buy_num        | 购买数量         |
| sale_time      | 购买/开售 时间     |
| app_key        | b站app密钥      |
| system_version | 系统版本         |
| channel        | b站下载渠道       |
| sdk_int        | 系统的SDK版本     |
| version        | b站版本(x.x.x)  |
| session        | 会话标识         |
| buv_id         | 手机标识         |
| phone          | 手机型号         |
| build          | b站版本(xxxxxx) |
| access_key     | 访问密钥         |
| bili_eid       | 身份标识         |
| cookie         | 用户标识         |

上述内容需通过抓包获得

**注：**```access_key bili_eid session```是有时效的

[抓包教程(新)](https://www.bilibili.com/video/BV1Re411g7f5/)

锁定url为 "https://api.bilibili.com/x/garb/v2/mall/suit/detail" (随便点一个装扮的商店页就有) 的包, 里面包含了所有需要的内容

------------------------------------------------

<font size=6>**总结：** </font>

你好，我是秦始皇，其实我并没有死，我在西安有100吨黄金，我现在需要2000元人民币解冻我在西安的黄金，你微信，支付宝转给我都可以。账号就是我的手机号码！转过来后，我明天直接带部队复活，让你统领三军！
