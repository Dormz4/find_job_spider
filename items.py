# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhaopinSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    job_name = scrapy.Field()
    url_job_id = scrapy.Field()
    company = scrapy.Field()
    finance_stage = scrapy.Field()
    company_label = scrapy.Field()
    eduction = scrapy.Field()
    job_description = scrapy.Field()
    city = scrapy.Field()
    district = scrapy.Field()
    work_year = scrapy.Field()
    salary = scrapy.Field()
    education = scrapy.Field()
    create_time = scrapy.Field()
    company_advantage = scrapy.Field()
    company_size = scrapy.Field()
    company_industry_field = scrapy.Field()  # 公司业务领域
    pass
