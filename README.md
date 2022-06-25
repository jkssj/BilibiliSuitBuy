# BilibiliSuitBuy

你好，我是秦始皇，其实我并没有死，我在西安有100吨黄金，我现在需要2000元人民币解冻我在西安的黄金，你微信，支付宝转给我都可以。账号就是我的手机号码！转过来后，我明天直接带部队复活，让你统领三军！

脚本很慢， 再优化它也是python比不过的

⭐︎⭐︎⭐︎不要看没有支付操作了，如果b币充足可以直接完成购买⭐︎⭐︎⭐︎

B站抢装扮脚本(一起烂吧)

抓包教程也在里面

设置BuyConfig

看config命名应该都看的懂吧，抓包软件一个一个复制就行

------------------------------------------------

抓包教程看这个 链接：[视频教程](https://pan.baidu.com/s/1epzhwbTpBNwNUMT0E-u_TQ?pwd=uvij)
提取码：uvij

补充: fiddler抓包要多一步

Tools -> Options -> HTTPS -> Actions -> Trust Root Certificate

------------------------------------------------

问: 抓包填的数据在哪找?

答: 锁定url为https://api.bilibili.com/x/garb/v2/mall/suit/detail(随便点一个装扮的商店页就有), 里面包含了所有需要的内容

accesskey,appkey,item_id在url里可以找到

其他东西都在访问头

------------------------------------------------

问: 抓完怎么运行?

答：安装[python](https://www.python.org/), 然后安装requests```pip install requests```, 填上刚刚抓包的内容, 把start的True改为Fasle就可以运行
