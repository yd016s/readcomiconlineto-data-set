import re
import tqdm
import time
import requests
import threading
import logging
from bs4 import BeautifulSoup
import pdb

URL = 'https://readcomiconline.to/ComicList'
MAX_PAGE = 10

def getLastPage():
    pass

def handler(soup) -> list:
    hrefs = []
    tr = soup.findAll('div', {'class':'col cover'})
    for i in tr:
        a = i.find('a')
        href = a['href']
        hrefs.append(href)
    return hrefs

def fetch_all_urls(max_page = MAX_PAGE) -> list:
    page = 1
    urls = []
    while page <= max_page:
        payload = { 
            'page':page
        }        
        source = requests.get(URL, params=payload)
        print(f'[*] Sraping urls from {source.url}')
        # TODO log info
        if source.ok:
            # TODO log info
            soup = BeautifulSoup(source.text,'html.parser')
            # TODO run threads threading
            # get urls from current page and concat
            urls = urls + handler(soup=soup)
        # increment page
        page += 1
    return urls

def fetch_metadata(soup) -> dict:
    meta = {}
    _barContent = soup.find('div', class_ = 'col info')
    # genre
    genre = []
    p = _barContent.findAll('p')
    p_genre = p[0]
    for i in p_genre.findAll('a'):
        genre.append(i.text)
    
    def get_form_to(_p_date):
        if _p_date.find('-') > 0:
            _from, _to = _p_date.split(' - ')
        else:
            _from = _p_date
            _to = None
        return (_from, _to)
    
    a_tag_text = lambda x : p[x].find('a').text
    clean_col = lambda x : x.strip('\n \r').partition(':\xa0')[2]
    _from, _to = get_form_to(clean_col(p[4].text))

    return {
            'title' : soup.find('h3').text,
            'genre' : genre,
            'publisher' : a_tag_text(1),
            'writer' : a_tag_text(2),
            'artist' : a_tag_text(3),
            'status' : clean_col(p[5].text),
            'views' : clean_col(p[6].text),
            'publication_date' : {
                    'from' : _from,
                    'to'   : _to
                    }
            }

def write_urls_to_file(filename):
    start_time = time.time()
    urls = fetch_all_urls()
    with open(filename,'w') as f:
        print(f'[$] Writing urls to {filename}.....')
        for i in urls:
            f.write(i + '\n') 
    print(f'[$] wrote {len(urls)} in {time.time() - start_time}!')

if __name__ == '__main__':
    write_urls_to_file('urls.txt')
