from tkinter.messagebox import YES
import scrapy
from scrapy import item
from datetime import datetime
import re

#base_two = 'https://www.jobs.bg/en/front_job_search.php?page={}'
#base = 'https://www.jobs.bg/en/front_job_search.php?subm=1&categories%5B%5D={}&page={}'


class SJobsBgSpider(scrapy.Spider):
    name = 's_jobs_bg'
    # allowed_domains = ['jobs.bg']
    #start_urls = [base.format(1, 1)]
    start_urls = [
        'https://www.jobs.bg/en/front_job_search.php?subm=1&categories%5B%5D=1']
    # def parse(self, response):
    #     # cat_list =[2,3]
    #     # for cat in cat_list:
    #     cat = 1
    #     yield scrapy.Request(url=response.url, callback=self.parse_cat, meta={'cat': cat})

    def parse(self, response):
        url = 'https://www.jobs.bg/en/front_job_search.php?subm=1&categories%5B%5D={}&page=1'
        # for cat in [13]:
        for cat in range(1, 60):
            url_cat = url.format(cat)
            if cat != 56:
                if cat == 57:
                    yield scrapy.Request(url_cat, self.parse_domain)
                else:
                    yield scrapy.Request(url_cat, self.parse_cat)

    def parse_domain(self, response):
        url = 'https://www.jobs.bg/en/front_job_search.php?subm=1&categories%5B%5D=56&domains%5B%5D={}&page=1'

        for dom in range(1, 27):
            url_dom = url.format(dom)
            yield scrapy.Request(url_dom, self.parse_cat)

    def parse_cat(self, response):
        # print(response.url)

        for job_url in response.xpath('//a[@class="black-link-b"]/@href').getall():
            item = {}
            item['categories'] = response.xpath(
                '//title/text()').get().split('"')[1].split('"')[0]
            yield scrapy.Request(url=job_url, callback=self.parse_job,  meta={'item': item})
        # print(job_url)

        # # PAGINATION
        # next_page = base.format(response.meta['cat'], int(
        #     response.url.rpartition('=')[-1])+1)
        next = int(response.url.rpartition('=')[-1])+1
        next_page = response.url.rpartition('=')[0] + '=' + str(next)
        total_results = response.xpath(
            '//span[@class="milestone-total"]/text()').get()
        # print((int(total_results)/20)+1)
        # if int(response.url.rpartition('=')[-1])+1 < (int(total_results)/20)+1:
        if total_results:
            yield scrapy.Request(url=next_page, callback=self.parse_cat)

    def parse_job(self, response):

        # print(response.url)
        item = response.meta['item']
        item['site'] = 'jobs.bg'
        item['job_title'] = response.xpath(
            '//span[@class="bold"]/text()').get()
        item['job_link'] = response.url
        item['date'] = datetime.strptime(self.clean_date(response.xpath(
            '//div[@class="date"]/text()').get()), "%d.%m.%Y").date()
        location = response.xpath(
            '//i[contains(text(),"location_on")]/parent::li/span/text()').get()
        if location:
            item['location'] = location.replace(' (view map)', '')
        salary = response.xpath(
            '//i[contains(text(),"paid")]/parent::li/span/b/text()').get()
        if salary:
            item['min_salary'] = salary.split(
                'of', maxsplit=1)[-1].split(maxsplit=1)[0]
            item['max_salary'] = salary.split(
                'to', maxsplit=1)[-1].split(maxsplit=1)[0]
        salary_type = response.xpath(
            '//i[contains(text(),"paid")]/parent::li/span/text()[2]').get()
        if salary_type:
            item['salary_type'] = salary_type[salary_type.find(
                '(')+1:salary_type.find(')')]
        item['schedule'] = response.xpath(
            '//i[contains(text(),"schedule")]/parent::li/span/text()').get()
        item['work_type'] = response.xpath(
            '//i[contains(text(),"work")]/parent::li/span/text()').get()

        item['languages'] = response.xpath(
            '//i[contains(text(),"language")]/parent::li/span/text()').get()
        item['organization'] = response.xpath(
            '//div[@class="pb-16 border-bottom-grey"]/text()').get().strip()
        item['org_desc'] = response.xpath(
            '//div[@class="pt-16 pb-8 border-bottom-grey"]/text()').get().strip()
        in_bg_since = response.xpath(
            '//i[contains(text(),"calendar_today")]/parent::li/text()[2]').get()
        if in_bg_since:
            item['in_bg_since'] = re.findall("\d+", in_bg_since)[0]
        emp = response.xpath(
            '//i[contains(text(),"people_alt")]/parent::li/text()[2]').get()
        if emp:
            item['employees'] = re.findall("\d+", emp)[0]
        intership = response.xpath(
            '//i[contains(text(),"school")]/parent::li/span/text()').get()
        if intership:
            item['intership'] = 'YES'
        else:
            item['intership'] = 'NO'
        remote_interview = response.xpath(
            '//i[contains(text(),"voice_chat")]/parent::li/span/text()').get()
        if remote_interview:
            item['remote_interview'] = 'YES'
        else:
            item['remote_interview'] = 'NO'
        item['remote'] = 'NO'
        remote = response.xpath(
            '//i[contains(text(),"home")]/parent::li/span/text()').get()
        if remote:
            item['remote'] = 'YES'
        remote = response.xpath(
            '//i/parent::li/span[contains(text(),"Fully remote work")]/text()').get()
        if remote:
            item['remote'] = 'YES'
        no_experience = response.xpath(
            '//i[contains(text(),"stairs")]/parent::li/span/text()').get()
        if no_experience:
            item['no_experience'] = 'YES'
        else:
            item['no_experience'] = 'NO'
        return item

    def clean_date(self, date):
        return date.split(',', 1)[0].strip()
