# coding=utf-8
from __future__ import unicode_literals, absolute_import
import scrapy
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
import urlparse
# import pdb
# pdb.set_trace()
from govbuy.apis.v1.gov_host import get_govs_purchase_urls_list_by_gov_name, get_host_id_by_host_url, \
    get_crawl_page_by_host_and_project_page_url
from ..items import DetailPageItem
import logging

logger = logging.getLogger(__name__)


class GovBuySpider(scrapy.Spider):
    name = 'govbuy_wan_huoshan_content'
    urls = set()
    flag = True
    sname = set()

    def start_requests(self):
        hosts = get_govs_purchase_urls_list_by_gov_name('霍山县人民政府网')  # 获取接口数据
        for url in hosts:
            yield scrapy.Request(url=url, callback=self.prase)

    def prase(self, response):
        url = response.url
        host_url = url.split('/')[2]
        title = response.xpath('//div[re:test(@class, "is-newstitle$")]').extract_first()  # 寿县
