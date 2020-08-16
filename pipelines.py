# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi

from DBHelper import DBHelper


class ZhaopinSpiderPipeline(object):
    def process_item(self, item, spider):
        # sql = "insert into film(name) values (%s)"
        # res = self.db.insert(item,sql)
        # if res ==0:
        #     print("插入",item,"失败")
        print(item.keys())
        if ('job_description' in item.keys()) == False:
        # if item['job_description'] == None:
            res = self.db.cursor.execute('''
                insert into job_list(`url_job_id`,`job_name`,`salary`,`work_year`,`education`,`company`,`company_advantage`,`company_industry_field`,`company_size`,\
                `finance_stage`,`company_label`,`city`,`district`,`create_time`) 
                values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
            '''%(item['url_job_id'],item['job_name'],item['salary'],item['work_year']\
                 ,item['education'],item['company'],item['company_advantage'],item['company_industry_field'],item['company_size'],item['finance_stage'],\
                 item['company_label'],item['city'],item['district'],item['create_time']))
            print("插入职位信息res:",res)
            self.db.connect.commit()
        else:
            print("命中要更新 职位详情 %d"%(item['url_job_id']))
            res = self.db.cursor.execute('''
                update job_list set job_description='%s' where url_job_id='%s';
            '''%(item['job_description'],item['url_job_id']))
            print("更新职位详情 res为:",res)
            self.db.connect.commit()
        return item

    def __init__(self):
        self.db = DBHelper()



    # @classmethod
    # def from_setting(cls,settings):
    #     db_params = dict(
    #         host=settings['MYSQL_HOST'],  # 读取settings中的配置
    #         db=settings['MYSQL_DBNAME'],
    #         user=settings['MYSQL_USER'],
    #         passwd=settings['MYSQL_PASSWD'],
    #         charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
    #         cursorclass=pymysql.cursors.DictCursor,
    #         use_unicode=False,
    #     )
    #
    #     db_pool = adbapi.ConnectionPool('pymysql', **db_params)
    #     return cls(db_pool)