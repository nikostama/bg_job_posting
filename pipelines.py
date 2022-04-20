# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from asyncio.windows_events import NULL
from dataclasses import replace
import site
from itemadapter import ItemAdapter
from sqlite3.dbapi2 import OperationalError
import sqlite3
import re
from datetime import date
from scrapy import Item
from deep_translator import (GoogleTranslator)
import winsound

WHITESPACE_RE = re.compile(r'\s+')


def normalise(text):
    r = text.upper()
    r = GoogleTranslator(source='bg', target='en').translate(text=r)
    # # r = r.replace('-', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').replace(
    # #     '„', ' ').replace('“', ' ').replace('"', ' ').replace(',', ' ').replace('+', ' ').replace('–', ' ').replace('.', ' ').replace('\u2116', 'o').strip()
    r = re.sub('[^a-zA-Z0-9А-Яа-я \n]', ' ', r)
    r = r.upper()
    return WHITESPACE_RE.sub(r' ', r)


def normalise_link(text):
    r = text.upper()
    # # # #r = GoogleTranslator(source='bg', target='en').translate(text=r)
    # # r = r.replace('-', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').replace(
    # #     '„', ' ').replace('“', ' ').replace('"', ' ').replace(',', ' ').replace('+', ' ').replace('–', ' ').replace('.', ' ').replace('\u2116', 'o').strip()
    r = re.sub('[^a-zA-Z0-9А-Яа-я \n]', ' ', r)
    r = r.upper()
    return WHITESPACE_RE.sub(r' ', r)


class BgJobPostingPipeline:
    def process_item(self, item, spider):
        return item


class SQLitePipeline(object):

    def open_spider(self, spider):

        #self.connection = sqlite3.connect("Undev.db")
        self.connection = sqlite3.connect("database.db")
        self.c = self.connection.cursor()
        try:
            self.c.execute('''
                    CREATE TABLE jobs(
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        duplicate TEXT,
                        norm_title TEXT,
                        job_link TEXT,
                        norm_link TEXT,
                        site TEXT,
                        location TEXT,
                        norm_location TEXT,
                        organization TEXT,
                        norm_org TEXT,
                        date DATE,
                        end_date DATE,
                        active TEXT,
                        min_salary INT,
                        max_salary INT,
                        intership TEXT,
                        work_type TEXT,
                        schedule TEXT,
                        remote TEXT,
                        remote_interview TEXT,
                        languages TEXT,
                        salary_type TEXT,
                        org_desc TEXT,
                        in_bg_since TEXT,
                        employees TEXT,
                        employees_worldwide TEXT,
                        no_experience TEXT,
                        year_founded TEXT,
                        sector TEXT,
                        central_office TEXT,
                        org_activity TEXT,
                        org_address TEXT,
                        tags TEXT,
                        categories TEXT
                    )

                ''')
            self.connection.commit()
        except sqlite3.OperationalError:
            pass

    def close_spider(self, spider):
        if 'zaplata' in spider.name:
            site = 'zaplata.bg'
            print('Zaplata.bg scraped!')
        elif 's_jobs_bg' in spider.name:
            site = 'jobs.bg'
            print('JOBS.bg scraped!')
        elif 's_jobs_dev_bg' in spider.name:
            site = 'dev.bg'
            print('Dev.bg scraped!')
        self.c.execute('''
                        UPDATE jobs SET end_date=?,active=? WHERE active=? AND site =?

                    ''', (date.today(), 'NO', 'YES', site,
                          ))
        self.connection.commit()
        self.c.execute('''
                        UPDATE jobs SET active=? WHERE (active=? OR active IS NULL) AND site =?

                    ''', ('YES', 'TEMP', site,
                          ))
        self.connection.commit()
        duration = 1000  # milliseconds
        freq = 440  # Hz
        winsound.Beep(freq, duration)
        self.connection.close()

    def process_item(self, item, spider):
        link = normalise_link(item['job_link']).strip()
        self.c.execute('''
                    SELECT id FROM jobs WHERE norm_link=?
                    ''', (link,))
        # result = self.c.fetchone()
        id = self.c.fetchone()
        self.connection.commit()
        if id:
            print('This job posting already exists ' + str(id[0]))
            print(id)
            # ACTIVE JOB POSTING
            self.c.execute('''
                         UPDATE jobs SET active=? WHERE id =?
                         
                     ''', ('TEMP', id[0],
                           ))

            # if item.get('remote') == 'YES' and item.get('site') == 'jobs.bg':
            #     self.c.execute('''
            #              UPDATE jobs SET remote=? WHERE id =?

            #          ''', ('YES', id[0],
            #                ))
            self.connection.commit()
        else:
            # NORMALIZATION
            norm = normalise(item.get('job_title')).strip()
            #print('^'+item.get['job_title'] + '^      ^' + norm + '^')
            if item.get('location'):
                norm_l = item.get('location').partition(',')[0]
                norm_l = normalise(norm_l).strip()
            else:
                norm_l = item.get('location')
            if item.get('organization'):
                norm_o = normalise(item.get('organization')).strip()
            else:
                norm_o = item.get('organization')
            # DEDUPLICATION
            self.c.execute('''
                    SELECT id FROM jobs WHERE norm_title=? AND (norm_location=? OR ((norm_location IS NULL OR ? IS NULL) AND (remote='YES' AND ?='YES' )) ) AND norm_org=?  AND JULIANDAY(date)-JULIANDAY(?)<3
                    ''', (norm, norm_l, norm_l, item.get('remote'), norm_o, item.get('date'),))
            # dupl_ids =
            # print(dupl_ids)
            if self.c.fetchone():
                dupl = 'YES'
            else:
                dupl = 'NO'

            # INSERT
            self.c.execute('''
                INSERT INTO jobs (title,norm_title,duplicate,job_link,norm_link,site,location,norm_location,organization,norm_org,date,min_salary,max_salary,intership,work_type,schedule,remote,remote_interview,languages,salary_type,org_desc,in_bg_since,employees,employees_worldwide,no_experience,year_founded,sector,central_office,org_activity,org_address,tags,categories) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

            ''', (
                item.get('job_title'),
                norm,
                dupl,
                item.get('job_link'),
                link,
                item.get('site'),
                item.get('location'),
                norm_l,
                item.get('organization'),
                norm_o,
                item.get('date'),
                item.get('min_salary'),
                item.get('max_salary'),
                item.get('intership'),
                item.get('work_type'),
                item.get('schedule'),
                item.get('remote'),
                item.get('remote_interview'),
                item.get('languages'),
                item.get('salary_type'),
                item.get('org_desc'),
                item.get('in_bg_since'),
                item.get('employees'),
                item.get('employees_worldwide'),
                item.get('no_experience'),
                item.get('year_founded'),
                item.get('sector'),
                item.get('central_office'),
                item.get('org_activity'),
                item.get('org_address'),
                item.get('tags'),
                item.get('categories'),
            ))

            self.connection.commit()
            return item
