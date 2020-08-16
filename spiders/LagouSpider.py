import datetime
import hashlib
import json
import random
import re
import time

import requests
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib import parse
import re

from scrapy import Selector, settings
import urllib.parse
# 记得 重写 sceapy.Spider的方法哦
from items import ZhaopinSpiderItem


# issue:
## 1.现在只能访问前10页，后面的页数就得更新cookie进行访问了
## 2.cookie的字段生成 逆的水土不服哟
# from settings import PROXIES


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

    User_Agent = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    ]



    def __init__(self, keyword):
        self.search_city = urllib.parse.quote('全国')
        self.keyword = keyword
        self.get_jsessionid_url = 'https://www.lagou.com/'
        self.get_other_cookie_url = 'https://a.lagou.com/json'
        self.url = 'https://www.lagou.com/jobs/list_' + self.keyword + '?labelWords=&fromSearch=true&suginput='
        self.url_real = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            # 'Referer': 'https://www.lagou.com/',
            # 'Proxy-Authorization':'Basic SEgxQ1JXMVQ4S1k3ODMxRDpEODA2MzZBMzMyMEMzMTY0',
        }
        self.headers_real = {
            # 'Proxy-Authorization':'Basic SEgxQ1JXMVQ4S1k3ODMxRDpEODA2MzZBMzMyMEMzMTY0',
            'Host': 'www.lagou.com',
            'Connection':'keep-alive',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Sec-Fetch-Dest':'document',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site':'same-origin',
            'Sec-Fetch-Mode':'navigate',
            'Sec-Fetch-User':'?1',
            # 'Referer':'https://www.lagou.com/utrack/trackMid.html?f=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%3FlabelWords%3D%26fromSearch%3Dtrue%26suginput%3D',
            'Referer':'https://www.lagou.com/',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6,zh-TW;q=0.5',
        }
        self.headers_real2 = {
            # 'Proxy-Authorization':'Basic SEgxQ1JXMVQ4S1k3ODMxRDpEODA2MzZBMzMyMEMzMTY0',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/jobs/list_'+urllib.parse.quote(self.keyword)+'?labelWords=&fromSearch=true&suginput=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        self.headers_job_detail={
            # 'Proxy-Authorization':'Basic SEgxQ1JXMVQ4S1k3ODMxRDpEODA2MzZBMzMyMEMzMTY0',
            'Host': 'www.lagou.com',
            'Connection':'keep-alive',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Sec-Fetch-Dest': 'document',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User':'?1',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6,zh-TW;q=0.5',
        }
        self.data = None
        self.cookies = dict()
        self.total_page = 0
        self.selector = None
        self.item_list = list()
        self.url_job_id_dict = dict()
        self.proxy_pool = [
            'http://1.199.30.215:9999',
        ]

    def init(self):
        self.data = requests.get(url=self.url, headers=self.headers, allow_redirects=False, verify=False)

    # 这里的cookie要自己算的  这里难就难在cookie里了
    def get_cookie(self):
        aa = "JSESSIONID=ABAAABAABFIAAAC1F7438516425F4D20CB140F729858824;" \
             " WEBTJ-ID=20200402204447-1713aec281c8f6-0a0fcf4e5da4da-f313f6d-2073600-1713aec281d834;" \
             " PRE_UTM=; PRE_HOST=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F;" \
             " user_trace_token=20200402204504-0cec3bc6-015a-4073-918d-788dd7e41871;" \
             " LGSID=20200402204504-663f7d39-0e14-49b8-968c-a66f620033c6;" \
             " PRE_SITE=https%3A%2F%2Fwww.lagou.com;" \
             " LGUID=20200402204504-e0c690e9-281d-4267-948e-e648e6990964;" \
             " _ga=GA1.2.1418999139.1585831506;" \
             " _gid=GA1.2.115742901.1585831506;" \
             " index_location_city=%E5%85%A8%E5%9B%BD;" \
             " Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1585831509;" \
             " TG-TRACK-CODE=index_search;" \
             " _gat=1;" \
             " sajssdk_2015_cross_new_user=1;" \
             " sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221713af49fdd54-000562fce12696-f313f6d-2073600-1713af49fde8ff%22%2C%22%24device_id%22%3A%221713af49fdd54-000562fce12696-f313f6d-2073600-1713af49fde8ff%22%7D;" \
             " X_MIDDLE_TOKEN=6ddddaca5f8750cf51929cf1fd35a293;" \
             " SEARCH_ID=32a68ab136fa4369ad25b419012f5b2c;" \
             " X_HTTP_TOKEN=40e54ad2df8fdefc9402385851311b7c7c084ad7d5;" \
             " Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1585832063; " \
             "LGRID=20200402205425-c115c8f2-f651-460b-9835-087a8f80e22c"
        # jessionid 通过https://www.lagou.com/ get 的 response 的set-cookie获取
        # user_token_id 通过https://a.lagou.com/show?t=24Hour%E7%83%AD%E9%97%A8&dl=https%3A%2F%2Fwww.lagou.com%2F&jids=6831474,6940359,6420452,5769670,5197467,6889714,6687401,6920032,6972326&z=0.9482728446266555&time=1585831487587
        ## get的 response 的set-cookie获取
        # WEBTJ-ID 为计算出来的 也就是 LGID

        # _ga、_gid也是计算出来的
        # X_MIDDLE_TOKEN=dadb2642a1da6c103509e9603e0a92cc; 为js计算出来的
        # SEARCH_ID 通过https://www.lagou.com/jobs/list_%E5%AE%89%E5%85%A8/p-city_0?&cl=false&fromSearch=true&labelWords=&suginput= 的set-cookie获取
        # X_HTTP_TOKEN 通过 计算得到的
        # LGSID LGUID LGRID 通过 https://a.lagou.com/json?lt=trackshow&a=aY00_idnull_0_9991_751&t=ad&v=0&dl=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%25E5%25AE%2589%25E5%2585%25A8%2Fp-city_0
        # %3F%26cl%3Dfalse%26fromSearch%3Dtrue%26labelWords%3D%26suginput%3D&dr=https%3A%2F%2Fwww.lagou.com&time=1585830368354 的 set-cookie获取

        user_trace_token = ''

        return self.cookies

    def start_requests(self):
        try:
            # yield scrapy.Request(url=self.get_jsessionid_url, method='GET', callback=self.parse_jssionid)
            yield scrapy.Request(url=self.url, method='GET',headers=self.headers, callback=self.parse_page)
        except:
            pass

    def parse_jssionid(self, response):
        if response.status == 200:
            cookie_list = response.headers.getlist('Set-Cookie');
            session_id = str(cookie_list[0]).split('JSESSIONID')[1].split(';')[0][1:];
            self.cookies['JSESSIONID'] = session_id

            # 这里进行获取其他cookie的参数
            'https://a.lagou.com/json?lt=trackshow&a=4k00_0001_0_7621_5052,4k00_0002_0_7664_2511,4k00_0003_0_7648_258,4k00_0004_0_7556_9953,4k00_0005_0_7673_3014,19pc_0001_0_8806_4646,19pc_0002_0_idnull_4860,19pc_0003_0_idnull_1230,19pc_0004_0_idnull_4748,19pc_0005_0_8800_3988,19pc_0006_0_8802_1309,19pc_0007_0_idnull_7996,19pc_0008_0_idnull_3856&t=ad&v=0&dl=https%3A%2F%2Fwww.lagou.com%2F&dr=https%3A%2F%2Fwww.lagou.com&time=1585904828562'

            yield scrapy.Request(url=self.get_other_cookie_url, method="GET", headers=self.headers, meta={
                'lt': 'trackshow',
                'a': '4k00_0001_0_7621_5052,4k00_0002_0_7664_2511,4k00_0003_0_7648_258,4k00_0004_0_7556_9953,4k00_0005_0_7673_3014,19pc_0001_0_8806_4646,19pc_0002_0_idnull_4860,19pc_0003_0_idnull_1230,19pc_0004_0_idnull_4748,19pc_0005_0_8800_3988,19pc_0006_0_8802_1309,19pc_0007_0_idnull_7996,19pc_0008_0_idnull_3856',
                't': 'ad',
                'v': 0,
                'dl': 'https://www.lagou.com/',
                'dr': 'https://www.lagou.com',
                'time': int(round(time.time() * 1000))
            }, callback=self.parse_cookie)

        else:
            print("获取session_id失败");
            return -1

    def parse_cookie(self, response):
        # print(response)
        # parse.quote()
        if response.status == 200:
            # 这里进行记录cookie
            cookies = response.headers.getlist('Set-Cookie')
            for cookies_item in cookies:
                data = str(cookies_item).split(';')[0].split('\'')[1];
                data_list = data.split('=')
                self.cookies[data_list[0]] = data_list[1]
            webtj_id = time.strftime("%Y%m%d", time.localtime(time.time())) + time.strftime("%H%M%S",time.localtime(time.time()))
            # 16位
            webtj_id += '-' + hex(int(str(random.random()).split('.')[1])).split('x')[1] + '-'
            # tmp =(hex(int(round(time.time() * 1000) / 100) + random.randint(100, 2000)).split('x')[1])
            tmp =str(random.random()).split('.')[1][0:14:]
            webtj_id+= tmp+ '-' + \
                        'f313f6d-' + '2073600-' + hex(int(str(random.random()).split('.')[1])).split('x')[1]
                        # (hex(int(round(time.time() * 1000) / 100) + random.randint(100, 2000)).split('x')[1]) + '-' + \
                        # 'f313f6d-' + '2073600-' + hex(int(str(random.random()).split('.')[1])).split('x')[1]

            # f313f6d生成代码:
            #         function
            #         no3()
            #         {
            #             function
            #         a(a, c)
            #         {
            #             var
            #         g, h = 0;
            #         for (g = 0; g < c.length; g++) h |= _[g] << 8 * g;
            #         return a ^ h
            #         }
            #         var
            #         i, c, g = navigator.userAgent, \
            #                   _ = [], \
            #                       h = 0;
            #         for (i = 0; i < g.length; i++) c = g.charCodeAt(i),
            #         _.unshift(255 & c),
            #         _.length >= 4 & & (h = a(h, _), _ =[]);
            #         return _.length > 0 & & (h = a(h, _)),
            #         h.toString(16)
            #
            # }
            # 2073600 生成代码
            #  var
                #  _ = String(screen.height * screen.width);
            #  _ = _ & & / \d
            #  {5, } /.test(_) ? _.toString(16): String(31242 * Math.random()).replace(".", "").slice(0, 8);

            self.cookies['WEBTJ-ID'] = webtj_id
            self.cookies['X_HTTP_TOKEN'] = self.lagou_calc_x_http_token(self.cookies['user_trace_token'])
            self.cookies['index_location_city'] = self.search_city
            timestamp1 = int(round(time.time() * 1000) / 100)
            self.cookies['_gid'] = 'GA1.2.590777851.' + str(timestamp1)
            self.cookies['_ga'] = 'GA1.2.413467336.' + str(timestamp1)
            timestamp2 = int(round(time.time() * 1000) / 100)
            self.cookies['Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6'] = timestamp2
            self.cookies['Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6'] = timestamp2
            self.cookies['TG-TRACK-CODE'] = 'index_search'
            self.cookies['PRE_LAND'] = 'https%3A%2F%2Fwww.lagou.com%2F'
            self.cookies['PRE_SITE']='https%3A%2F%2Fwww.lagou.com'

            # yield scrapy.Request(url=self.url, method="GET", headers=self.headers_real,
            #                      cookies={
            #                          'JSESSIONID':self.cookies['JSESSIONID'],
            #                          'user_trace_token':self.cookies['user_trace_token'],
            #                          'LGSID':self.cookies['LGSID'],
            #                          'PRE_UTM': self.cookies['PRE_UTM'],
            #                          'PRE_HOST': self.cookies['PRE_HOST'],
            #                          'PRE_SITE': self.cookies['PRE_SITE'],
            #                          'PRE_LAND': self.cookies['PRE_LAND'],
            #                          'LGUID': self.cookies['LGUID'],
            #                          'LGRID': self.cookies['LGRID'],
            #                          'WEBTJ-ID': self.cookies['WEBTJ-ID'],
            #                          'X_HTTP_TOKEN': self.cookies['X_HTTP_TOKEN'],
            #                          'index_location_city':self.cookies['index_location_city'],
            #                          'TG-TRACK-CODE': self.cookies['TG-TRACK-CODE'],
            #                          '_gid': self.cookies['_gid'],
            #                          '_ga': self.cookies['_ga'],
            #                          'Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6': self.cookies['Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6'],
            #                          'Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6': self.cookies['Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6'],
            #                      },
            #                      callback=self.parse_page,dont_filter=True)
            cc = ''
            # for key in self.cookies.keys():
            #     aa = key
            #     cc += key+'='+str(self.cookies[key])+';'
            # self.headers_real['Cookie'] = cc[:-1]

            cc += 'JSESSIONID='+self.cookies['JSESSIONID']+'; '+\
                'WEBTJ-ID='+self.cookies['WEBTJ-ID']+'; '+\
                'X_HTTP_TOKEN='+self.cookies['X_HTTP_TOKEN']+'; '+\
                'index_location_city='+self.cookies['index_location_city']+'; '\
                'PRE_UTM=; PRE_HOST=; '+'PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; user_trace_token='+\
                self.cookies['user_trace_token']+'; LGSID='+self.cookies['LGSID']+\
                '; PRE_SITE='+self.cookies['PRE_SITE']+'; LGUID='+self.cookies['LGUID']+\
                '; LGRID='+self.cookies['LGRID']+'; _gid='+self.cookies['_gid']+\
                '; _ga='+self.cookies['_ga']+'; _gat=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6='+\
                str(self.cookies['Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6'])+'; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6='+\
                str(self.cookies['Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6'])+'; TG-TRACK-CODE='+self.cookies['TG-TRACK-CODE']
            # self.headers_real['Cookie'] = cc


            # yield scrapy.Request(url=self.url, method="GET", headers=self.headers_real,
            #                      cookies=self.cookies,callback=self.parse_page, dont_filter=True)
            yield scrapy.Request(url=self.url, method="GET", headers=self.headers_real,
                                 callback=self.parse_page, dont_filter=True)

            # self.headers_real['Cookie'] = self.cookies;
            # yield scrapy.Request(url=self.url, method="GET", headers=self.headers_real,
            #                      callback=self.parse_page, dont_filter=True)


        else:
            print("获取其他cookie值失败");
            return -2;

    def lagou_calc_x_http_token(self, user_trace_token):
        ori_data = 'HTTP_JS_KEY' + user_trace_token
        md5_data = hashlib.md5(ori_data.encode('utf-8'))
        num_list = list()
        md5_data = md5_data.hexdigest()
        is_record = False
        for i in range(0, len(md5_data)):
            if is_record is True:
                is_record = False
                # print(md5_data[i - 1], md5_data[i])
                num = int(md5_data[i - 1], 16) * 0x10 + int(md5_data[i], 16)
                num_list.append(num)
            if i % 2 == 0:
                is_record = True

        res = ''
        for i in range(0, len(num_list)):
            res += hex(num_list[i] >> 0x4).split('x')[1] + hex(num_list[i] & 0xf).split('x')[1]

        return res

    # 这里获取职位的页数，记得修改cookie 的search_id哦
    def parse_page(self, response):
        if response.status == 200:
            # 获取 总页数
            self.selector = Selector(text=response._body)
            res = self.selector.xpath('//span').re('(<span.?\sclass=\".?span.?\stotalNum.?\".*?>\d+.?</span>)')
            self.total_page = int(str(res).split('>')[1].split('<')[0])
            # re_res = re.search('<span.?\sclass=\".?span.?\stotalNum.?\".*?>\d+.?</span>', response.text)
            # self.total_page =int(str(re_res).split('>')[1].split('<')[0])
            if self.total_page == 0:
                print("该关键字的页数为0，请核对")
                return
            # 这里进行获取列表的职位摘要，要用代理进行访问避免拒访IP
            for page_idx in range(1, self.total_page + 1):
            # for page_idx in range(1, 3):
                # cookie = self.get_cookie()
                # print(cookie)
                self.headers_real['Referer'] = 'https://www.lagou.com/jobs/list_'+urllib.parse.quote(self.keyword)+'?labelWords=&fromSearch=true&suginput='
                self.headers_real['User-Agent'] = LagouSpider.User_Agent[random.randint(0, 3)]
                # proxy = self.proxy_pool[random.randint(0,len(self.proxy_pool)-1)]
                # print("使用代理:%s"%proxy)
                print("访问第%d页"%page_idx)
                yield scrapy.FormRequest(url=self.url_real, headers=self.headers_real,
                                         formdata={
                                             "first": "true",
                                             "pn": str(page_idx),
                                             'kd': self.keyword,
                                         }, dont_filter=True, callback=self.parse_each_page_result,errback=self.err_parse_each_page_result)

                time.sleep(random.randint(1,2))
        else:
            print("获取'%s'的总页数失败" % self.keyword)
            yield scrapy.Request(url=self.url, method="GET", headers=self.headers_real,
                                 callback=self.parse_page, dont_filter=True)
            # return -3

    def err_parse_each_page_result(self,failure):
        print(failure)

    # 先这样请求完数据，然后再通过数据进行做数据的筛选,
    ## 想过记录参数顺序，但是还是觉得没必要
    def parse_each_page_result(self, response):
        try:
            print(response)
            self.print_response_header(response);
            json_res = json.loads(str(response.body, 'utf-8'))
            if json_res['success'] == True:
                print("访问成功")

                job_list = json_res['content']['positionResult']['result']
                for idx in range(0, json_res['content']['positionResult']['resultSize']):
                    item = ZhaopinSpiderItem()
                    item['job_name'] = job_list[idx]['positionName']
                    self.url_job_id_dict[json_res['content']['showId']] = job_list[idx]['positionId']
                    item['url_job_id'] = job_list[idx]['positionId']
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
                        company_label_list += company_label
                    item['company_label'] = company_label_list
                    item['company_advantage'] = job_list[idx]['positionAdvantage']
                    item['company_size'] = job_list[idx]['companySize']
                    item['company_industry_field'] = job_list[idx]['industryField']  # 公司业务领域
                    # print(item)
                    yield item

                # show_id = json_res['content']['showId']
                # # for idx in range(0, json_res['content']['positionResult']['resultSize']):
                # url = 'https://www.lagou.com/jobs/' + str(6729894) + '.html?show=' + show_id
                # yield scrapy.Request(url=url, method='GET', headers=self.headers, callback=self.parse_job_details)
                #


                # # 接下来是访问 职位的详细要求的
                # show_id = json_res['content']['showId']
                # for idx in range(0, json_res['content']['positionResult']['resultSize']):
                for key in self.url_job_id_dict.keys():
                    self.headers_job_detail['User-Agent'] = LagouSpider.User_Agent[random.randint(0,3)]
                    # self.headers['Cookie'] = ''
                    url = 'https://www.lagou.com/jobs/' + str(self.url_job_id_dict[key]) + '.html?show=' + key
                    'source=home_hot&i=home_hot-0'
                    # url = 'https://www.lagou.com/jobs/' + str(self.url_job_id_dict[key]) + '.html?source=home_hot&i=home_hot-0'
                    # proxy = self.proxy_pool[random.randint(0,len(self.proxy_pool)-1)]
                    # print("使用代理2:%s"%proxy)
                    yield scrapy.Request(url=url,method='GET',headers=self.headers_job_detail,
                                         # meta={
                                         #    # 'dont_redirect': True,
                                         #    # 'handle_httpstatus_list': [302],
                                         #     {'proxy': random.randint(0, len(PROXIES) - 1)},
                                         # },
                                         callback=self.parse_job_details)
                    print("进行请求",url)
                    # res = requests.get(url=url,headers=self.headers_job_detail,verify=False)
                    # print(res.text)
                    time.sleep(10)

            else:
                print("获取职位列表失败了")
        except Exception as e:
            print(e)

    def print_response_header(self,response):
        for i in response.headers:
            print("%s:%s"%(i.decode(),response.headers.getlist(i.decode())[0].decode()))

    def parse_job_details(self, response):
        # 这里将得到的数据更新回原来的数据库不就好了吗。
        print(response)
        # for i in response.headers:
        #     print("%s:%s"%(i.decode(),response.headers.getlist(i.decode())[0].decode()))
        self.print_response_header(response);
        if response.status == 200:
            print("得到职位详情")
            self.selector = Selector(text=response._body)
            job_advantage_list = self.selector.xpath('//dd').re('<dd.?\sclass=\".?job-advantage.?\">[\s\S]*?</dd>')[0].split('\n')
            job_advantage =  job_advantage_list[1].split('>')[1].split('<')[0]+job_advantage_list[2].split('>')[1].split('<')[0]
            job_description_list = self.selector.xpath('//div').re('<div.?\sclass=\".?job-detail.?\">[\s\S]*?</div>')[0].split('\n')
            job_description = ''
            for dd in job_description_list:
                if dd.find('div')>0 or dd.find('</div>')>0:
                    continue
                job_description +=dd+'\n'

            item = ZhaopinSpiderItem()
            item['job_name'] = '1'
            item['company'] = '1'
            item['finance_stage'] ='1'
            item['city'] = '1'
            item['district'] = '1'
            item['work_year'] = '1'
            item['salary'] = '1'
            item['education'] = '1'
            item['create_time'] = '1'
            item['company_label'] = '1'
            item['company_advantage'] = '1'
            item['company_size'] = '1'
            item['company_industry_field'] = ''
            item['job_description'] =job_advantage+'\n'+job_description
            item['url_job_id'] = int(response._url.split('/')[4].split('?')[0].split('.')[0])
            yield item
        elif response.status==302:
            print("获取职位详情失败,重新来")
            self.headers_job_detail['Referer'] = 'https://sec.lagou.com/verify.html?e=2&f='+response._url;
            yield scrapy.Request(url=response._url, method='GET', headers=self.headers_job_detail,
                                 # meta={
                                 #    # 'dont_redirect': True,
                                 #    # 'handle_httpstatus_list': [302],
                                 #     {'proxy': random.randint(0, len(PROXIES) - 1)},
                                 # },
                                 callback=self.parse_job_details, dont_filter=True)


            # return -3

