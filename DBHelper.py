import time

import pymysql
from scrapy.utils.project import get_project_settings
from twisted.enterprise import adbapi


class DBHelper():
    def __init__(self):
        settings = get_project_settings()  # 获取settings配置，设置需要的信息

        # dbparams = dict(
        #     host=settings['MYSQL_HOST'],  # 读取settings中的配置
        #     db=settings['MYSQL_DBNAME'],
        #     user=settings['MYSQL_USER'],
        #     passwd=settings['MYSQL_PASSWD'],
        #     charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
        #     cursorclass=pymysql.cursors.DictCursor,
        #     use_unicode=False,
        # )
        # # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        # dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        #
        # self.dbpool = dbpool

        self.connect = pymysql.connect(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True
        )

        self.cursor = self.connect.cursor()

        self.pre_init()

    # 进行创建数据表
    def pre_init(self):
        res = self.cursor.execute('''create table if not exists `job_list`(
            `id` int unsigned auto_increment,
            `url_job_id` int not null comment '招聘网该职位的id',
            `job_name` varchar(30) not null comment '职位名',
            `salary` varchar(30) not null comment '薪水区间',
            `work_year` varchar(30) not null comment '工作年限',
            `education` varchar(10) not null comment '学历要求',
            `company` varchar(100) not null comment '公司名',
            `company_advantage` varchar(60) not null comment '公司优势',
            `company_industry_field` varchar(60) not null comment '公司服务领域',
            `company_size` varchar(30) not null comment '公司规模',
            `finance_stage` varchar(10) not null comment '融资阶段',
            `company_label` varchar(100) not null comment '公司标签',
            `city` varchar(10) not null comment '工作城市',
            `district` varchar(10) not null comment '城市中的区',
            `job_description` varchar(1200)  comment '职位简介',
            `create_time` TIMESTAMP not null comment '发布职位时间',
            PRIMARY KEY ( id )
        )ENGINE=InnoDB DEFAULT CHARSET=utf8;''')

        print(res)

    # def connect(self):
    #     return self.dbpool

    # 创建数据库
    def insert(self, item,sql):
        try:
            # sql = "insert into tech_courses(title,image,brief,course_url,created_at) values(%s,%s,%s,%s,%s)"
            # 调用插入的方法
            query = self.dbpool.runInteraction(self._conditional_insert, sql, item)
        except Exception as e:
            # 调用异常处理方法
            query.addErrback(self._handle_error)

        return item

    # 写入数据库中
    def _conditional_insert(self, tx, sql, item):
        item['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                           time.localtime(time.time()))
        params = (item["title"], item['image'], item['brief'],
                  item['course_url'], item['created_at'])
        tx.execute(sql, params)

    # 错误处理方法

    def _handle_error(self, failue):
        print('--------------database operation exception!!-----------------')
        print(failue)