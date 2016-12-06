# coding=utf-8
from __future__ import unicode_literals, absolute_import
import urlparse
import scrapy
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from govbuy.apis.v1.gov_host import get_govs_purchase_urls_list, get_host_id_by_host_url, \
    get_crawl_page_by_host_and_project_page_url
from ..items import DetailPageItem
import logging

logger = logging.getLogger(__name__)
"""
定时 执行 爬虫 任务 抓取 采购列表的 第一页 和 第二页 列表信息 填充 数据库
"""


class GovBuySpider(scrapy.Spider):
    name = 'govbuy_wan_timing_list'  # 定时蜘蛛
    urls = set()
    flag = True
    wan_shucheng_extractor = LxmlLinkExtractor(allow='/tmp/xxgklist2.shtml')
    sname = set()
    xpath_map = {
        'xxgk.yuan.gov.cn': '//li[re:test(@class, "mc$")]//a',
        'www.shucheng.gov.cn': '//li[re:test(@class, "mc$")]//a',
        'www.shouxian.gov.cn': '//div[re:test(@class, "is-tda$")]//a',
        'www.ahjinzhai.gov.cn': '//li[re:test(@class, "mc$")]//a',
        'www.ja.gov.cn': '//li[re:test(@class, "mc$")]//a',
        'www.ahhuoshan.gov.cn': '//div[re:test(@class, "is-tda$")]//a',
        'www.huoqiu.gov.cn': '//li[re:test(@class, "mc$")]//a'
    }

    def start_requests(self):
        hosts = get_govs_purchase_urls_list()  # 获取接口数据(所有列表页面地址)
        for url in hosts:
            yield scrapy.Request(url=url, callback=self.prase)

    def prase(self, response):
        url = response.url
        host_url = url.split('/')[2]
        if len(self.urls) == 0 and self.flag:
            self.flag = False
            template = (url[:-1] + '{0}')
            for i in xrange(1, 2):
                url = template.format(i)
                self.urls.add(url)
        links = response.xpath(self.xpath_map[host_url])  # 这里根据域名来找xpath map 字符串 属于定制内容
        for index, link in enumerate(links):
            shref = link.xpath('@href').extract()[0]
            sname = link.xpath('text()').extract()[0]
            crawl_page = DetailPageItem()
            host_id = get_host_id_by_host_url('http://' + host_url.strip())
            record = get_crawl_page_by_host_and_project_page_url(host_id, shref)
            if not record and sname not in self.sname:
                crawl_page['host_id'] = host_id
                crawl_page['host_url'] = host_url
                crawl_page['logogram'] = sname
                crawl_page['project_page_url'] = shref
                crawl_page.save()
                self.sname.add(sname)
        for inner_url in self.urls:
            yield scrapy.Request(url=inner_url, callback=self.prase)
