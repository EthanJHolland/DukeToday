import requests
from tqdm import tqdm
from time import sleep
from csv import DictWriter
from bs4 import BeautifulSoup
from urllib.request import urlopen

#soup helper methods
def getSoup(url):
    data = requests.get(url).text
    return BeautifulSoup(data, 'html.parser')

def writeSoup(filename, url):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(getSoup(url).prettify())

#attribute extractors
def getArticle(page, articleSoup):
    return {
        'page': page,
        'title': getTitle(articleSoup) or '',
        'subtitle': getSubtitle(articleSoup) or '',
        'snippet': getSnippet(articleSoup) or '',
        'date': getDate(articleSoup) or '',
        'tags': getTags(articleSoup) or [],
        'source': getSource(articleSoup) or '',
        'link': getLink(articleSoup) or ''
    }

def getTitle(soup):
    return soup.find('header').find('h1','story-title').get_text(strip=True)

def getSubtitle(soup):
    return soup.find('header').find('p','story-subtitle').get_text(strip=True)

def getSnippet(soup):
    tag = soup.find('p','story-snippet')
    if tag:
        return tag.get_text(strip=True)

def getDate(soup):
    return soup.find('small', 'story-published-info').time.attrs['datetime']

def getTags(soup):
    tags = []
    for linkTag in soup.find_all('a','topic-link'):
        tag = linkTag.attrs['href']
        tags.append(tag[tag.rindex('/')+1:])
    return tags

def getSource(soup):
    text = soup.find('a','story-link').get_text(strip=True)
    if text == 'Read':
        return 'Duke Today'
    elif text.startswith('Read on'):
        return text[text.index('Read on')+len('Read on')+1:]

def getLink(soup):
    return soup.find('a','story-link').attrs['href']

#main
if __name__=='__main__':
    url = 'https://today.duke.edu/search/story?keys=&sort_by=created&sort_order=DESC&page={}'

    #init
    page = 0
    pbar = tqdm(total=10401, position=0, ncols=80, mininterval=1.0)
    keys = ['page','date','title','subtitle','snippet','tags','source','link'] #set key order to ensure consistency when appending to csv

    with open('out.csv', 'w') as f:
        w = DictWriter(f, keys) 
        w.writeheader()

        while True:
            soup = getSoup(url.format(page))
            if not soup.find('article'):
                break #reached end
            
            for articleSoup in soup.find_all('article'):
                w.writerow(getArticle(page, articleSoup))

            page+=1 #increment page
            pbar.update(1)

            sleep(2)
        