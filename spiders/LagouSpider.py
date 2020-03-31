import datetime
import json
import re
import time

import requests
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib import parse
import re

from scrapy import Selector

# 记得 重写 sceapy.Spider的方法哦
from items import ZhaopinSpiderItem


class LagouSpider(scrapy.Spider):
    name = "lagou"
    # 域名
    allowed_domain = ["lagou.com"]
    # start_urls=[
    #     "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
    #     "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    # ]
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        'Sec-Fetch-Dest': 'empty',
        'X-Requested-With': 'XMLHttpRequest',
    }

    def __init__(self,keyword):
        self.keyword = keyword
        self.url = 'https://www.lagou.com/jobs/list_'+self.keyword+'?labelWords=&fromSearch=true&suginput='
        self.url_real = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        self.headers_real = {
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        self.data = None
        self.cookies = None
        self.total_page = 0
        self.selector = None

    def init(self):
        self.data = requests.get(url=self.url, headers=self.headers, allow_redirects=False, verify=False)

    def get_cookie(self):
        return self.cookies

    def start_requests(self):
        try:
            # start_urls=[
            #     "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false"
            # ]
            data = {
                "first": "true",
                "pn": '1',
                'kd': self.keyword,
            }

            yield scrapy.Request(url=self.url,method="GET", headers=self.headers, callback=self.parse)

            # response = requests.post(url=self.url_real, headers=self.headers_real, data=data, verify=False,
            #                          cookies=self.get_cookie())
            # self.parse(response)
            # yield scrapy.Request(url=self.url_real, method='POST', headers=self.headers_real, cookies=self.get_cookie(),
            #                      body=json.dumps(data), callback=self.parse)
            # yield scrapy.FormRequest(url=self.url_real,headers=self.headers_real,cookies=self.get_cookie(),
            #                      formdata={
            #                          "first": "true",
            #                          "pn": '1',
            #                          'kd': self.keyword,
            #                      },dont_filter=True,callback=self.parse)
        except:
            pass


    def parse(self, response):
        # print(response)
        # parse.quote()
        if response.status == 200:
            # 这里进行记录cookie
            self.cookie = response.headers.getlist('Set-Cookie')
            # 获取 总页数
            self.selector = Selector(text=response._body)
            res = self.selector.xpath('//span').re('(<span.?\sclass=\".?span.?\stotalNum.?\".*?>\d+.?</span>)')
            self.total_page =int(str(res).split('>')[1].split('<')[0])
            # re_res = re.search('<span.?\sclass=\".?span.?\stotalNum.?\".*?>\d+.?</span>', response.text)
            # self.total_page =int(str(re_res).split('>')[1].split('<')[0])
            if self.total_page==0:
                print("该关键字的页数为0，请核对")
                return
            for page_idx in range(1,self.total_page+1):
                yield scrapy.FormRequest(url=self.url_real, headers=self.headers_real, cookies=self.get_cookie(),
                                     formdata={
                                         "first": "true",
                                         "pn": str(page_idx),
                                         'kd': self.keyword,
                                     }, dont_filter=True, callback=self.parse_result)
                time.sleep(0.1)

    # 先这样请求完数据，然后再通过数据进行做数据的筛选,
    ## 想过记录参数顺序，但是还是觉得没必要
    def parse_result(self,response):
        print("断不住吗")
        print(response)
        json_res = json.loads(str(response.body,'utf-8'))
        if json_res['success'] == True:
            print("访问成功")
            job_list = json_res['content']['positionResult']['result']
            for idx in range(0,json_res['content']['positionResult']['resultSize']):
                item = ZhaopinSpiderItem()
                item['job_name'] = job_list[idx]['positionName']
                item['url_job_id'] =job_list[idx]['positionId']
                item['company'] = job_list[idx]['companyFullName']
                item['finance_stage'] = job_list[idx]['financeStage']
                item['city'] = job_list[idx]['city']
                item['district'] = job_list[idx]['district']
                item['work_year'] = job_list[idx]['workYear']
                item['salary'] = job_list[idx]['salary']
                item['education'] = job_list[idx]['education']
                item['create_time'] = job_list[idx]['createTime']
                company_label_list = ''
                for company_label in job_list[idx]['companyLabelList']:
                    company_label_list+=company_label
                item['company_label'] = company_label_list
                item['company_advantage'] = job_list[idx]['positionAdvantage']
                item['company_size'] = job_list[idx]['companySize']
                item['company_industry_field'] = job_list[idx]['industryField'] #公司业务领域
                yield item

        else:
            print("获取职位列表失败了")

