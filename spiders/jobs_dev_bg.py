import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class JobsDevBgSpider(CrawlSpider):
    name = 'jobs_dev_bg'
    allowed_domains = ['dev.bg']
    start_urls = ['https://dev.bg/?s=&post_type=job_listing']

    rules = (
        # Job posting link
        Rule(LinkExtractor(
            restrict_xpaths='//div[@class="job-list-item  "]/div[@class="inner-left company-logo-wrap"]/a[@class="overlay-link"]'), callback='parse_item', follow=True),
        # Pagination
        # Rule(LinkExtractor(restrict_xpaths='//a[@class="next page-numbers"]'))
    )

    def parse_item(self, response):
        item = {}
        item['job_title'] = response.xpath(
            '//h6[@class="job-title"]/text()').get()
        item['job_link'] = response.url
        item['organization'] = response.xpath(
            '//span[@class="company-name  "]/text()').get()
        item['location'] = response.xpath(
            '//span[@class="badge  no-padding  "]/text()').get() or None
        item['date'] = response.xpath(
            '//li[@class="date-posted"]/time/@datetime').get()
        # item['categories'] = response.xpath(
        #     '//div[@class="categories-wrap"]/a/text()').getall()
        return item
