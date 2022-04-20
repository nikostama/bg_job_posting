import scrapy
from scrapy import item
from datetime import datetime


class SJobsDevBgSpider(scrapy.Spider):
    name = 's_jobs_dev_bg'
    allowed_domains = ['dev.bg']
    start_urls = ['https://dev.bg']

    def parse(self, response):
        # print(response.url)
        for jobs in response.xpath('//div[@id="section-category-block"]/div/div/a[@class="category-name"]/@href').getall():
            yield scrapy.Request(url=jobs, callback=self.parse_cat)

    def parse_cat(self, response):

        for jobs in response.xpath('//div[@class="job-list-item  "]/div[@class="inner-left company-logo-wrap"]/a/@href').getall():
            yield scrapy.Request(url=jobs, callback=self.parse_job)
           # print(jobs)

        for jobs in response.xpath('//div[@class="job-list-item  is-premium "]/div[@class="inner-left company-logo-wrap"]/a/@href').getall():
            yield scrapy.Request(url=jobs, callback=self.parse_job)

        # PAGINATION
        next_page = response.xpath(
            '//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_cat)

    def parse_job(self, response):
        # print(response.url)
        item = {}
        item['site'] = 'dev.bg'
        item['job_title'] = response.xpath(
            '//h6[@class="job-title ab-title-placeholder ab-cb-title-placeholder"]/text()').get()
        item['job_link'] = response.url
        item['organization'] = response.xpath(
            '//span[@class="company-name  "]/text()').get()
        item['location'] = response.xpath(
            '//span[@class="badge  no-padding  "]/text()').get() or None
        item['date'] = datetime.strptime(response.xpath(
            '//li[@class="date-posted"]/time/@datetime').get(), "%Y-%m-%d").date()
        item['categories'] = response.xpath(
            '//a[@class="pill"][1]/text()').get()
        remote = response.xpath(
            '//span[@class="badge green bold remote "]').get()
        if remote:
            item['remote'] = 'YES'
        else:
            item['remote'] = 'NO'
        org = response.xpath('//div[@class="box box-company"]/p/a/@href').get()
        if org:
            yield scrapy.Request(url=org, callback=self.parse_org, meta={'item': item}, dont_filter=True)
        else:
            yield item
        # yield item

    def parse_org(self, response):
        item = response.meta['item']
        item['year_founded'] = response.xpath(
            '//p[@class="p-big-16 without-margin" and contains(text(),"Година на основаване:")]/following-sibling::p/text()').get()
        item['in_bg_since'] = response.xpath(
            '//p[@class="p-big-16 without-margin" and contains(text(),"От кога има офис в България?")]/following-sibling::p/text()').get()
        item['employees'] = response.xpath(
            '//p[@class="p-big-16 without-margin" and contains(text(),"Служители в България:")]/following-sibling::p/text()').get()
        item['employees_worldwide'] = response.xpath(
            '//p[@class="p-big-16 without-margin" and contains(text(),"Служители в глобален мащаб:")]/following-sibling::p/text()').get()

        item['sector'] = response.xpath(
            '//h3[@class="h3-style-3" and contains(text(),"Сектор")]/following-sibling::p/text()').get()
        item['central_office'] = response.xpath(
            '//h3[@class="h3-style-3" and contains(text(),"Централен офис")]/following-sibling::p/text()').get()
        item['org_activity'] = response.xpath(
            '//h3[@class="h3-style-3" and contains(text(),"Дейност")]/following-sibling::p/text()').get()
        item['org_address'] = response.xpath(
            '//h3[@class="h3-style-3" and contains(text(),"Адрес")]/following-sibling::div/p/text()').get()

        yield item
