# -*- coding: utf-8 -*-
"""
author : Bisakh Mondal
@file : main.py
"""
import requests
from bs4 import BeautifulSoup, Comment
import argparse
import pprint
import json
import unicodedata
import pickle
import re
import datetime


class NewsDict:
    """
        Python Dictionary wrapper for storing unique field of article url such that
        if the user is running the script continuously it can maintain a unique articles.

    """

    def __init__(self, load=True):
        self.dict = {}
        self.filename = 'dump.pickle'
        if load:
            self.load()
        print(self.dict)

    def load(self):
        try:
            with open(self.filename, 'rb') as f:
                self.dict = pickle.load(f)
        except Exception as e:
            print(e)
            pass

    def dump(self):
        for k, v in self.dict.items():
            if v == 0:
                self.dict.pop(k)
            else:
                self.dict[k] = 0
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.dict, f)
        except Exception as e:
            pass

    def check(self, id):
        if self.dict.get(id) is None:
            self.dict[id] = 1
            return False
        self.dict[id] += 1
        return True


URL = 'https://www.telegraphindia.com/'
page = requests.get(URL)
print('Request sent...')

soup = BeautifulSoup(page.content, 'html.parser')

# Deleting commented out elements from DOM
for child in soup.body.div.children:
    if isinstance(child, Comment):
        child.extract()

result = soup.find('div', class_='container mainContainer uk-background-default pt-3')

print('Parsing...')
article_cols = result.find_all('div', class_='row')

nDict = NewsDict()


# For parsing string from the body with unicode decoding and unwanted character removal.
def format_string(s):
    op = unicodedata.normalize('NFKD', s.strip().lower()).encode('ascii', 'ignore')
    op = str(op, 'utf-8')
    op = re.sub('[\n\t\r]+', ' ', op)
    return op


# if No description for an article found in paragraph tag, check twice if the description is
# wrapped in another html element.
def format_list(lists):
    op = [x for x in lists if len(x.strip()) > 2]
    return op


def parse_text(element):
    p = element.find('p')
    if p is not None:
        return format_string(p.text)
    string_lists = format_list(list(element.strings))
    if len(string_lists) >= 2:
        return format_string(string_lists[-1])
    return ''


# check if it is really an article or some nuisance advertise
def is_article(hyperlink):
    if hyperlink.find('h2') is None:
        return None
    link = hyperlink['href']
    h2 = hyperlink.find('h2')

    return link, format_string(h2.text), parse_text(hyperlink)


# extract texts from articles.
def get_article(hyperlinks):
    card = []
    for hyperlink in hyperlinks:
        article = is_article(hyperlink)
        if article is not None:
            uid = int(article[0].split('/')[-1])
            if nDict.check(uid) is False:
                card.append(
                    {
                        'link': article[0],
                        'headline': article[1],
                        'text': article[2],
                        'time': datetime.datetime.utcnow().strftime('%s')
                    }
                )
    return card


# extracting all anchor tag within the body
article_links = []
for cols in article_cols:
    articles = cols.find_all('a', href=True)
    article_links.extend(articles)

print(len(article_links))
cards = get_article(article_links)
news = {
    URL: cards
}
print('Parsing complete. :)')
print(len(cards))
# pprint.pprint(cards)

# Maintaining all information in json file.
with open('parse.json', 'w+') as j:
    try:
        data = json.load(j)

    except:
        data = {
            URL: []
        }
    data[URL].extend(news[URL])
    json.dump(data, j, indent=4)

nDict.dump()
