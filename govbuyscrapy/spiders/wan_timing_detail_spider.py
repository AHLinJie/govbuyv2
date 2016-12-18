# coding=utf-8
from __future__ import unicode_literals, absolute_import
import re
import urlparse
import scrapy
from bs4 import BeautifulSoup
from govbuy.apis.v1.gov_host import get_uncrawled_purchase_urls, crawled_detail_page_content
from ..items import DetailPageItem
import logging

logger = logging.getLogger(__name__)
"""
定时 执行 爬虫 任务 抓取 采购 页面内容
"""


class GovBuySpider(scrapy.Spider):
    name = 'govbuy_wan_timing_detail'  # 内容页面定时蜘蛛
    xpath_map = {
        'xxgk.yuan.gov.cn': {
            'title': '//div[re:test(@class, "wztit$")]//text()',
            'content': '//div[re:test(@class, "wzcon$")]//text()'
        },
        'www.ja.gov.cn': {
            'title': '//div[re:test(@class, "wztit$")]//text()',
            'content': '//div[re:test(@class, "wzcon$")]//p//text()'
        },
        'www.ahhuoshan.gov.cn': {
            'title': '//div[re:test(@class, "is-newstitle$")]//text()',
            'content': '//div[re:test(@class, "is-newscontnet$")]//text()'
        },
        'www.ahjinzhai.gov.cn': {
            'title': '//h1[re:test(@class, "newstitle$")]//text()',
            'content': '//div[re:test(@class, "newscontnet xxgkwz minh500$")]//text()'
        },
        'www.shucheng.gov.cn': {
            'title': '//h1[re:test(@class, "wztit$")]//text()',
            'content': '//div[re:test(@class, "wzcon$")]//text()'
        },
        'www.shouxian.gov.cn': {
            'title': '//div[re:test(@class, "m-article$")]//h2//text()',
            'content': '//div[re:test(@class, "m-article$")]//text()'
        },
        'www.huoqiu.gov.cn': {
            'title': '//h1[re:test(@class, "newstitle$")]//text()',
            'content': '//div[re:test(@class, "newscontnet$")]//text()'
        },
        'www.lazfcg.gov.cn': {
            'title': '//div[re:test(@class, "reportTitle$")]//h1//text()',
            'content': '//div[re:test(@class, "frameReport$")]//text()'
        }
    }

    def start_requests(self):
        page_urls = get_uncrawled_purchase_urls()  # 获取接口数据(所有列表页面地址)
        # page_urls = ['http://www.shouxian.gov.cn/openness/detail/content/5482bcfd592c20c26c61bc9d.html']
        for url in page_urls:
            yield scrapy.Request(url=url, callback=self.prase)

    def prase(self, response):
        url = response.url
        host_url = url.split('/')[2]
        title_xpath = self.xpath_map.get(host_url).get('title')
        content_xpath = self.xpath_map.get(host_url).get('content')
        if not (title_xpath and content_xpath):
            return
        project_name = response.xpath(title_xpath).extract_first()
        text_list = response.xpath(content_xpath).extract()
        data = []
        for i in text_list:
            if '\n' not in i:
                i = '\n' + i  # 添加换行
            if i:
                i = i.replace(' ', '')  # 删除空格
            data.append(i)
        content = ''.join(data)
        p1 = re.compile('(\\t*)*\\t')
        tmp = re.sub(p1, '\n', content)  # 替换掉\r 为\n
        p1 = re.compile('(\\r*)*\\r')
        tmp = re.sub(p1, '\n', tmp)  # 替换掉\r 为\n
        p2 = re.compile('(\\n*)*\\n')
        content = re.sub(p2, '\n', tmp)  # 将多个 \n换为一个\n
        crawled_detail_page_content(url, project_name, content)
