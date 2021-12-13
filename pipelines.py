# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlite3.dbapi2 import OperationalError
import sqlite3


class BgJobPostingPipeline:
    def process_item(self, item, spider):
        return item


class SQLitePipeline(object):

    def open_spider(self, spider):
        self.connection = sqlite3.connect("database.db")
        self.c = self.connection.cursor()
        try:
            self.c.execute('''
                    CREATE TABLE jobs(
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        job_link TEXT,
                        location TEXT,
                        organization TEXT,
                        date DATE,
                        min_salary INT,
                        max_salary INT
                    )
                    
                ''')  # CONSTRAINT PK PRIMARY KEY (title, organization)
            # self.c.execute('''
            #         CREATE TABLE tags(
            #             name TEXT PRIMARY KEY
            #         )

            #     ''')  # tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            # self.c.execute('''
            #         CREATE TABLE jobs_tags(
            #             tag_name TEXT,
            #             job_id INT,
            #             FOREIGN KEY(tag_name) REFERENCES tags(name),
            #             FOREIGN KEY(job_id) REFERENCES jobs(id)
            #            )

            #     ''')  # FOREIGN KEY(tag_id) REFERENCES jobs(job_title, organization),
            #    FOREIGN KEY(job_id) REFERENCES tags(tag_name)

            self.connection.commit()
        except sqlite3.OperationalError:
            pass

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.c.execute('''
                    SELECT title FROM jobs WHERE title=? AND organization=?
        ''', (item['job_title'], item['organization'],))
        #result = self.c.fetchone()
        if self.c.fetchone():
            print('Duplicate item found')
            # Already exists
            pass
        else:
            self.c.execute('''
                INSERT INTO jobs (title,job_link,location,organization,date,min_salary,max_salary) VALUES(?,?,?,?,?,?,?)

            ''', (
                item.get('job_title'),
                item.get('job_link'),
                item.get('location'),
                item.get('organization'),
                item.get('date'),
                item.get('min_salary'),
                item.get('max_salary'),

            ))
            # TAGS
            # self.c.execute('''
            #             SELECT MAX(id) FROM jobs

            # ''')
            # my_id = int(self.c.fetchone()[0])
            # print(my_id)

            # for i in item.get('tags'):
            #     self.c.execute('''
            #         SELECT name FROM tags WHERE name=?
            #     ''', (i,))
            #     # print(self.c.fetchone())
            #     if self.c.fetchone():
            #         print('Duplicate tag found')
            #         pass
            #     else:
            #         self.c.execute('''
            #             INSERT INTO tags (name) VALUES(?)

            #         ''', (
            #             i,
            #         ))
            #     self.c.execute('''
            #         INSERT INTO jobs_tags (tag_name, job_id) VALUES(?,?)

            #     ''', (
            #         i, my_id,
            #     ))

            self.connection.commit()
            return item
