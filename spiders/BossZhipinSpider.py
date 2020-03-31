import scrapy



# 由于 app版本的需要登录账号才能访问接口，所以这里就爬网页端的，不过网页端需要解析html哦
class BossZhipinSpider(scrapy.Spider):
    name="zhipin"
    # 域名
    allowed_domain=["zhipin.com"]
    start_urls=[
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]

    def parse(self,response):
        filename=response.url.split("/")[-2]
        with open(filename,"wb") as f:
            f.write(response.body)

