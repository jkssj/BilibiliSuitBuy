# BilibiliSuitBuy

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

答: 锁定url为https://api.bilibili.com/x/garb/v2/mall/suit/detail的包, 里面包含了所有需要的内容

------------------------------------------------

问: 抓完怎么运行?

答：安装[python](https://www.python.org/), 然后安装requests```pip install requests```, 填上刚刚抓包的内容, 把start的True改为Fasle就可以运行
