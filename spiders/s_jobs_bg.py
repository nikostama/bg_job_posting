from tkinter.messagebox import YES
import scrapy
from scrapy import item
from datetime import datetime
import re

base = 'https://www.jobs.bg/en/front_job_search.php?page={}'


class SJobsBgSpider(scrapy.Spider):
    name = 's_jobs_bg'
    #allowed_domains = ['jobs.bg']
    start_urls = [base.format(1)]

    def parse(self, response):
        # print(response.url)
        for job_url in response.xpath('//div[@class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7"]/a/@href').getall():
            yield scrapy.Request(url=job_url, callback=self.parse_job)
           # print(job_url)

        # PAGINATION
        next_page = base.format(int(response.url.rpartition('=')[-1])+1)

        if int(response.url.rpartition('=')[-1])+1 is not 101:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_job(self, response):

        print(response.url)
        item = {}
        item['job_title'] = response.xpath(
            '//span[@class="bold"]/text()').get()
        item['job_link'] = response.url
        item['date'] = datetime.strptime(self.clean_date(response.xpath(
            '//div[@class="pb-8 color-gray-3"]/text()').get()), "%d.%m.%Y")
        location = response.xpath(
            '//i[contains(text(),"location_on")]/parent::li/text()[2]').get()
        if location:
            item['location'] = location.replace(' (view map)', '')
        salary = response.xpath(
            '//i[contains(text(),"paid")]/parent::li/text()[2]').get()
        if salary:
            item['min_salary'] = salary.split(
                'of', maxsplit=1)[-1].split(maxsplit=1)[0]
            item['max_salary'] = salary.split(
                'to', maxsplit=1)[-1].split(maxsplit=1)[0]
            item['salary_type'] = salary[salary.find('(')+1:salary.find(')')]
        item['schedule'] = response.xpath(
            '//i[contains(text(),"schedule")]/parent::li/text()[2]').get()
        item['work_type'] = response.xpath(
            '//i[contains(text(),"work")]/parent::li/text()[2]').get()

        item['languages'] = response.xpath(
            '//i[contains(text(),"language")]/parent::li/text()[2]').get()
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
            '//i[contains(text(),"school")]/parent::li/text()[2]').get()
        if intership:
            item['intership'] = 'YES'
        else:
            item['intership'] = 'NO'
        remote_interview = response.xpath(
            '//i[contains(text(),"voice_chat")]/parent::li/text()[2]').get()
        if remote_interview:
            item['remote_interview'] = 'YES'
        else:
            item['remote_interview'] = 'NO'
        remote = response.xpath(
            '//i[contains(text(),"home")]/parent::li/text()[2]').get()
        if remote:
            item['remote'] = 'YES'
        else:
            item['remote'] = 'NO'

        no_experience = response.xpath(
            '//i[contains(text(),"stairs")]/parent::li/text()[2]').get()
        if no_experience:
            item['no_experience'] = 'YES'
        else:
            item['no_experience'] = 'NO'
        return item

    def clean_date(self, date):
        return date.split(',', 1)[0].strip()
