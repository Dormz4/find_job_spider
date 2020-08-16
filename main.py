from scrapy import cmdline
import sys

if __name__ == '__main__':
    # 设置好 查询关键词 ,譬如 "逆向"
    #
    # cmdline.execute("scrapy crawl dmoz".split())
    # cmdline.execute('scrapy crawl dmoz -o items.json'.split())]
    try:
        if sys.argv[1]!=None:
            keyword = sys.argv[1]
        else:
            keyword = input('请输入岗位关键字:')
    except Exception as e:
        print(e)

    # cmdline.execute(("scrapy crawl lagou -a keyword="+keyword).split())
    cmdline.execute(("scrapy crawl zhipin -a keyword="+keyword).split())


    # 剩下的就交给数据库进行检索，以及数据可视化

