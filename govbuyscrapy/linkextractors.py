# coding=utf-8
from __future__ import unicode_literals, absolute_import
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import logging

logger = logging.getLogger(__name__)


def test():
    extractor = LxmlLinkExtractor(allow='article')  # allow 填写正则匹配　或者　正则匹配列表
