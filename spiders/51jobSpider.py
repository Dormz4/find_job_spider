import scrapy

# 这个可以全国搜索
class _51JobSpider(scrapy.Spider):
    name = "51job"
    allowed_domain = ["51job.com"]