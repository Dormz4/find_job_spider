from scrapy import cmdline

if __name__ == '__main__':
    # 设置好 查询关键词 ,譬如 "逆向"
    #
    # cmdline.execute("scrapy crawl dmoz".split())
    # cmdline.execute('scrapy crawl dmoz -o items.json'.split())
    keyword = input('请输入岗位关键字:')
    cmdline.execute(("scrapy crawl lagou -a keyword="+keyword).split())


    # 剩下的就交给数据库进行检索，以及数据可视化

