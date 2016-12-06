# -*- coding: utf-8 -*-
# scrapy crawl dmoz -o items.json -t json 写数据到json文件
import scrapy
from scrapy_djangoitem import DjangoItem
from govbuy.models import CrawlPage


def serialize_test(value):
    return 'test-%s' % value


class DmozItem(scrapy.Item):
    title = scrapy.Field(serializer=serialize_test)


class DetailPageItem(DjangoItem):
    django_model = CrawlPage
