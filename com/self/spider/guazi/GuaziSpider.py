#!/usr/bin/env python3
# encoding:utf-8
import requests
import time, random
from pyquery import PyQuery as pq

# 请求头 cookie 必须需要加上,爬前request网址试下可以get到全内容不,不能的话换下cookie
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate,br',
           'Accept-Language': 'zh-CN,zh;q=0.9',
           'Cache-Control': 'no-cache',
           'Connection': 'keep-alive',
           'Cookie': 'uuid=c8dda799-7600-40e5-a020-2d28e308ee40; ganji_uuid=9450925418870829074157; cityDomain=bj; lg=1; clueSourceCode=10103000312%2300; sessionid=74fcd60e-6f05-42e0-c6fa-a59a54ec5666; cainfo=%7B%22ca_s%22%3A%22pz_baidu%22%2C%22ca_n%22%3A%22tbmkbturl%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22%22%2C%22ca_campaign%22%3A%22%22%2C%22ca_kw%22%3A%22%25e7%2593%259c%25e5%25ad%2590%2520%25e4%25ba%258c%25e6%2589%258b%25e8%25bd%25a6%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22scode%22%3A%2210103000312%22%2C%22ca_transid%22%3A%22%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22ca_i%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_a%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%22c8dda799-7600-40e5-a020-2d28e308ee40%22%2C%22sessionid%22%3A%2274fcd60e-6f05-42e0-c6fa-a59a54ec5666%22%7D; antipas=V74531896215Q6su1212o76O0p; preTime=%7B%22last%22%3A1554171276%2C%22this%22%3A1554115250%2C%22pre%22%3A1554115250%7D',
           'Host': 'www.guazi.com',
           'Pragma': 'no-cache',
           'Referer': 'https://www.guazi.com/bj/buy',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}


class GuaziSpider():

    # 初始化爬虫
    def __init__(self):
        # 目标url
        self.baseurl = 'https://www.guazi.com'
        '''
        在进行接口测试的时候，我们会调用多个接口发出多个请求，在这些请求中有时候需要保持一些共用的数据，例如cookies信息。
        requests库的session对象能够帮我们跨请求保持某些参数，也会在同一个session实例发出的所有请求之间保持cookies。
        '''
        self.s = requests.Session()
        self.s.headers = headers
        # 本地ip被封的话启用该处ip代理池
        # self.s.proxies = proxies
        self.start_url = 'https://www.guazi.com/bj/buy/'
        self.infonumber = 0  # 用来记录爬取了多少条信息用

    # get_page用来获取url页面
    def get_page(self, url):
        return pq(self.s.get(url).text)

    # page_url用来生成第n到第m页的翻页链接
    def page_url(self, n, m):
        page_start = n
        page_end = m
        # 新建空列表用来存翻页链接
        page_url_list = []
        for i in range(page_start, page_end + 1, 1):
            base_url = 'https://www.guazi.com/www/buy/o{}/#bread'.format(i)
            page_url_list.append(base_url)

        return page_url_list

    # detail_url用来抓取详情页链接
    def detail_url(self, start_url):
        # 获取star_url页面
        content = self.get_page(start_url)
        # 解析页面,获取详情页链接content=pq(self.s.get(start_url).text)
        for chref in content('ul[@class="carlist clearfix js-top"]  > li > a').items():
            url = chref.attr.href
            detail_url = self.baseurl + url
            yield detail_url

    # carinfo用来抓取每辆车的所需信息
    def carinfo(self, detail_url):
        content = self.get_page(detail_url)
        d = {}
        d['model'] = content('h2.titlebox').text().strip()  # 车型
        d['registertime'] = content('ul[@class="assort clearfix"] li[@class="one"] span').text()  # 上牌时间
        d['mileage'] = content('ul[@class="assort clearfix"] li[@class="two"] span').text()  # 表显里程
        d['secprice'] = content('span[@class="pricestype"]').text()  # 报价
        d['newprice'] = content('span[@class="newcarprice"]').text()  # 新车指导价(含税)
        d['address'] = content('ul[@class="assort clearfix"]').find('li'). \
            eq(2).find('span').text()  # 上牌地
        d['displacement'] = content('ul[@class="assort clearfix"]'). \
            find('li').eq(3).find('span').text()  # 排量
        return d

    def run(self, n, m):
        page_start = n
        page_end = m
        with open('guazidata{}to{}.txt'.format(page_start, page_end), 'a', encoding='utf-8') as f:
            for pageurl in self.page_url(page_start, page_end):
                print(pageurl)
                print("让俺歇歇10-15秒啦，太快会关小黑屋的！")
                time.sleep(random.randint(10, 15))
                for detail_url in self.detail_url(pageurl):
                    print(detail_url)
                    d = self.carinfo(detail_url)
                    f.write(d['model'] + ',')
                    f.write(d['registertime'] + ',')
                    f.write(d['mileage'] + ',')
                    f.write(d['secprice'] + ',')
                    f.write(d['newprice'] + ',')
                    f.write(d['address'] + ',')
                    f.write(d['displacement'] + '\n')
                    time.sleep(0.3)
                    self.infonumber += 1
                    print('爬了%d辆车,continue!' % self.infonumber)
                print('+' * 10)


if __name__ == '__main__':
    gzcrawler = GuaziSpider()
    # 这儿改数字,例如:爬取第1页到第100页的信息
    gzcrawler.run(1, 2)
