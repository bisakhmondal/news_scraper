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

    # Serializing byte stream to dictionary
    def load(self):
        try:
            with open(self.filename, 'rb') as f:
                self.dict = pickle.load(f)
        except Exception as e:
            pass

    # Deserializing dictionary for future reference
    def dump(self):
        lis = []
        for k, v in self.dict.items():
            if v == 0:
                lis.append(k)
            else:
                self.dict[k] = 0
        [self.dict.pop(k) for k in lis]
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


BASE_URL = 'https://www.telegraphindia.com'
URL = BASE_URL + '/world/page-{}'

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
        return format_string(string_lists[-2])
    return ''


# check if it is really an article or some nuisance advertise
def is_article(hyperlink):
    if hyperlink.find('h2') is None:
        return None
    link = hyperlink['href']
    h2 = hyperlink.find('h2')

    return link, format_string(h2.text), parse_text(hyperlink)


def is_article_for_row(row):
    if row.find('h2') is None:
        return None
    h2 = row.find('h2')
    date = row.find('span').text
    link = h2.find('a', href=True)['href']
    return link, format_string(h2.text), parse_text(row), date


# extract texts from articles.
def get_article(hyperlinks):
    card = []
    for hyperlink in hyperlinks:
        article = is_article(hyperlink)
        if article is not None and article[2] != '':
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


def get_article_from_row(rows):
    card = []
    for row in rows:
        article = is_article_for_row(row)
        if article is not None and article[2] != '':
            uid = int(article[0].split('/')[-1])
            if nDict.check(uid) is False:
                card.append(
                    {
                        'link': BASE_URL + article[0],
                        'headline': article[1],
                        'text': article[2],
                        'time': article[3]
                    }
                )
    return card


def MAKE_REQUEST(num_pages):
    cards = []
    for idx in range(1, num_pages + 1):
        page = requests.get(URL.format(idx))
        print('Request sent...')

        soup = BeautifulSoup(page.content, 'html.parser')

        # Deleting commented out elements from DOM
        for child in soup.body.div.children:
            if isinstance(child, Comment):
                child.extract()

        result = soup.find('div', class_='container uk-background-default pt-3 mainContainer')

        print('Parsing Page {} ....'.format(idx))
        article_cols = result.find_all('div', class_='row')
        # article_cols = article_cols.find_all('div',class_='row')
        # extracting all anchor tag within the body
        articles = []
        for cols in article_cols:
            article = cols.find_all('div', class_='row')
            articles.extend(article)

        print(len(articles))
        with open('a.txt', 'w') as f:
            f.write(str(articles))

        cards.extend(get_article_from_row(articles))
    print('Parsing complete. :)')
    return cards


news = {
    BASE_URL: MAKE_REQUEST(10)
}
print('Total new articles found :->', len(news[BASE_URL]))

# Maintaining all information in json file.
with open('parse.json', 'r+', encoding='utf-8', errors='ignore') as j:
    try:
        data = json.load(j, strict=False)

    except:
        data = {
            BASE_URL: []
        }

data[BASE_URL].extend(news[BASE_URL])

with open('parse.json', 'w', encoding='utf-8', errors='ignore') as j:
    json.dump(data, j, indent=4)
    # To store dictionary state for next run
    nDict.dump()
