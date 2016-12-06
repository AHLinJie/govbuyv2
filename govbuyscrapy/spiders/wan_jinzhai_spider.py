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
    name = 'govbuy_wan_jinzhai'
    urls = set()
    flag = True
    wan_shucheng_extractor = LxmlLinkExtractor(allow='/tmp/xxgklist2.shtml')  # 金寨县
    sname = set()

    def start_requests(self):
        hosts = get_govs_purchase_urls_list_by_gov_name('金寨县人民政府网')  # 获取接口数据
        for url in hosts:
            yield scrapy.Request(url=url, callback=self.prase)

    def prase(self, response):
        url = response.url
        host_url = url.split('/')[2]
        if len(self.urls) == 0 and self.flag:
            self.flag = False
            extractor = self.wan_shucheng_extractor
            links = extractor.extract_links(response)
            max_page = int(urlparse.parse_qs(urlparse.urlparse(links[-1].url).query)['pp'][0])
            template = (url[:-1] + '{0}')
            for i in xrange(1, max_page + 1):
                url = template.format(i)
                self.urls.add(url)
        links = response.xpath('//li[re:test(@class, "mc$")]//a')  # 金寨
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
