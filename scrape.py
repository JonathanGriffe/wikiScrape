from lxml import html
import requests
import psycopg2
import re
import time

class wikipedia_scraper(object):
    
    def __init__(self, init_url, pages, database):
        self.init_url = init_url
        self.pages = pages
        self.conn = psycopg2.connect(host="localhost", database="wikiuser", user="wikiuser", password="myPGPW")
        self.cur = self.conn.cursor()
        self.regT = re.compile('^/wiki/')
    
    def get_urls(self, parent_url, url_tree, parent_id, cur, distance):
        '''
        Helper function to grab all links from the url tree and insert into database
        '''
        urlRegexp = re.compile(parent_url)
        for child in url_tree.iter():
            if child.tag == 'a':
                link = child.get('href')
                if link and self.regT.match(link) and not urlRegexp.match(link):
                    cur.execute('''INSERT INTO Pages (url, topic, distance, investigated) VALUES (%s, %s, %s, false) ON CONFLICT DO NOTHING''', (link, link[6:], distance, ))
                    cur.execute('''SELECT id FROM Pages WHERE url=%s''', (link,))
                    id = cur.fetchone()[0]
                    cur.execute('''INSERT INTO Links (parent_id, child_id)
                        VALUES ( %s, %s ) ON CONFLICT DO NOTHING''', (parent_id, id, ) )
                    self.conn.commit()
        cur.execute('''UPDATE Pages SET investigated=true WHERE id=%s''', (parent_id, ))
        self.conn.commit()

    def reset_db_tables(self):
        '''
        Resets tables of database
        '''
        self.cur.execute('''
        DROP TABLE IF EXISTS Links;
        DROP TABLE IF EXISTS Pages;
        
        CREATE TABLE Links (
            id  SERIAL NOT NULL PRIMARY KEY UNIQUE,
            topic INTEGER,
            parent_id INTEGER,
            child_id INTEGER,
            UNIQUE (parent_id, child_id)
        );
        
        CREATE TABLE Pages (
            id SERIAL NOT NULL PRIMARY KEY UNIQUE,
            url TEXT UNIQUE,
            topic TEXT,
            distance INTEGER,
            investigated BOOLEAN
        );
        ''')
        self.conn.commit()

    def scrapePage(self, url, page_id, distance):
        '''
        scrapes one page
        '''
        page = requests.get('https://fr.wikipedia.org' + url)
        tree = html.fromstring(page.content)
        # all the links in the main content in the class 'mw-content-ltr'
        tree_body = tree.find_class('mw-content-ltr')
        try:
            tree_body=tree_body[0] # in list type for some reason
            self.get_urls(url, tree_body, page_id, self.cur, distance + 1) # grab the urls from the tree
        except: print("err")
        
    def scrape(self, init_url):
        self.cur.execute('''INSERT INTO Pages (url, topic, distance, investigated) VALUES (%s, %s, %s, false)''', (init_url, init_url[6:], 0))
        self.conn.commit()
        self.resumeScrapping()

    def resumeScrapping(self):
        self.cur.execute('''SELECT min(distance) FROM Pages WHERE investigated=false''')
        distance = self.cur.fetchone()[0] - 1
        while 1:
            distance += 1
            print(f"distance: {distance}")
            self.cur.execute('''SELECT id, url FROM Pages WHERE investigated=false AND distance=%s''', (distance, ))
            rows = self.cur.fetchall()
            for row in rows:
                id, url = row
                self.scrapePage(url, id, distance)
                time.sleep(0.1)

    def close_connections(self):
        '''
        Close connections to database
        '''
        self.cur.close()
        self.conn.close()

if __name__ == "__main__":
    pages = 200
    init_url = '/wiki/%C3%89cole_nationale_sup%C3%A9rieure_des_mines_de_Paris'
    scraper = wikipedia_scraper(init_url, pages, 'localhost:5432')
    scraper.resumeScrapping()
    scraper.close_connections()