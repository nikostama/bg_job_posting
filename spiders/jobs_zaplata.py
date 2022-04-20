import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.trackref import NoneType
from datetime import datetime


class JobsZaplataSpider(CrawlSpider):
    name = 'jobs_zaplata'
    allowed_domains = ['www.zaplata.bg']
    start_urls = [
        'https://www.zaplata.bg/en/search/?q=&city_name=&city=&city_distance=0&price=200%3B10000&cat%5B%5D=1000&go=']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=(
            '//div[@class="listItems"]/ul[@class="listItem "]/li[@class="c2"]/a')), callback='parse_item', follow=True),
        # Pagination
        Rule(LinkExtractor(restrict_xpaths='(//a[@class="next"])[1]'))

    )

    def parse_item(self, response):
        item = {}
        item['site'] = 'zaplata.bg'
        item['job_title'] = response.xpath(
            "//h1[@class='title']/text()").get()
        item['job_link'] = response.url
        item['location'] = self.clean(response.xpath(
            '//strong[contains(text(),"Place of employment")]/following-sibling::node()[position()=2]/descendant::*/text()').getall())
        item['organization'] = response.xpath(
            '//strong[contains(text(),"Organization")]/following-sibling::node()[position()=2]/descendant::*/text()').get()
        categories = response.xpath(
            '//strong[contains(text(),"Category")]/following-sibling::node()[position()=2]/descendant::*/text()').getall()
        item['categories'] = ','.join(categories)
        level = response.xpath(
            '//strong[contains(text(),"Level")]/following-sibling::node()[position()=2]/descendant::*/text()').getall()
        item['intership'] = 'NO'
        for i in level:
            if 'Interns/Students' in i:
                item['intership'] = 'YES'
        # date = response.xpath(
        #     '//div[@class="statistics"]/span/text()').get()
        # if date:
        item['date'] = datetime.strptime(response.xpath(
            '//div[@class="statistics"]/span/text()').get(), "%d %B %Y").date()
        tags = response.xpath(
            '//div[@class="tags"]/a/text()').getall()
        item['tags'] = ','.join(tags)
        if (response.xpath('//span[@class="clever-link searchRes"]/text()').get() is not None):
            salary = self.split_dash(self.clean(response.xpath(
                '//span[@class="clever-link searchRes"]/text()').get().split('\n')))
            item['min_salary'] = salary[0].split()[0]
            item['max_salary'] = salary[1].split()[0]
        else:
            item['min_salary'] = None
            item['max_salary'] = None

        type = response.xpath(
            '//strong[contains(text(),"Type of employment")]/following-sibling::node()/a/text()').getall()
        item['remote'] = 'NO'
        for i in type:
            if 'Full time' in i:
                try:
                    if item['schedule']:
                        item['schedule'] += ', Full time'
                except:
                    item['schedule'] = 'Full time'
            if 'Part-time' in i:
                try:
                    if item['schedule']:
                        item['schedule'] += ', Part time'
                except:
                    item['schedule'] = 'Part time'
            if 'Telework' in i:
                item['remote'] = 'YES'
            if 'Permanent' in i:
                try:
                    if item['work_type']:
                        item['work_type'] += ', Permanent'
                except:
                    item['work_type'] = 'Permanent'
            if 'Temporary/Seasonal/Project' in i:
                try:
                    if item['work_type']:
                        item['work_type'] += ', Temporary'
                except:
                    item['work_type'] = 'Temporary'

        return item

    def clean(self, list):
        s = ''
        for i in list:
            s += i.strip(' \n ').replace('/', ',')
        return s

    def split_dash(self, str):
        return str.split('-')
