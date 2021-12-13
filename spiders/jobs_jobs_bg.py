import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime


class JobsJobsBgSpider(CrawlSpider):
    name = 'jobs_jobs_bg'
    allowed_domains = ['www.jobs.bg']
    start_urls = [
        'https://www.jobs.bg/change_lang.php?new_lang=en&rpath=/front_job_search.php&']

    rules = (
        # Job posting link
        Rule(LinkExtractor(
            restrict_xpaths='//a[@class="card__title mdc-typography mdc-typography--headline6 text-overflow"]'), callback='parse_item', follow=True),
        # Pagination
        # Rule(LinkExtractor(
        #     restrict_xpaths='(//a[@class="pathlink"][position()=15])[1]'))
    )

    def parse_item(self, response):
        # print(response.url)
        item = {}
        item['job_title'] = response.xpath(
            '//span[@style="color:#66c1ff;;"]/following-sibling::node()[2]/text()').get()
        item['organization'] = response.xpath(
            '//a[@class="company_link"]/text()').get()
        item['job_link'] = response.url
        item['date'] = datetime.strptime(self.clean_date(response.xpath(
            '//td[@class="explainGray"]/text()').get()), "%d.%m.%Y")
        # item['skills'] = response.xpath(
        #    '//li[@style="list-style-type: none; border-bottom: none; float: left; padding: 10px 10px 0px 0;"]/table/tbody/tr/td/text()').get()
        # item['desc'] = response.xpath(
        #     '//td[@style="font-style:italic;"]/text()').getall()

        # SALARY
        salary = response.xpath(
            '//td[@style="font-style:italic;"]/span/b/text()').get()
        if salary:
            item['min_salary'] = salary.split(
                'from', maxsplit=1)[-1].split(maxsplit=1)[0]
            item['max_salary'] = salary.split(
                'to', maxsplit=1)[-1].split(maxsplit=1)[0]
        # LOCATION
        item['location'] = None
        # desc = self.sep(response.xpath(
        #     '//td[@style="font-style:italic;"]/text()').get())
        # for i in desc:
        desc = response.xpath(
            '//td[@style="font-style:italic;"]/text()').get()
        if 'location' in desc:
            item['location'] = desc.split(
                'location', maxsplit=1)[-1].split(maxsplit=1)[0].replace(',', '').replace(';', '')
        return item

    def clean_date(self, date):
        return date.split(',', 1)[0]

    def sep(self, str):
        str = str.split(';')

        return str
