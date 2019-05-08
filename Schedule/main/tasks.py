from __future__ import absolute_import, unicode_literals
import os
import re
import multiprocessing
from pprint import pprint
from time import perf_counter
from urllib.parse import parse_qs

import django
import requests
from bs4 import BeautifulSoup
from celery import shared_task, group

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Schedule.settings")
django.setup()
from .models import Apartment


# URL = 'https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&maxarea=30&minarea=20&offer_type=flat&region=1&room1=1&type=4'
URL = 'https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&maxarea=25&minarea=20&offer_type=flat&region=1&room1=1&type=4'
# URL = 'https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&region=1&room1=1&type=4'

def get_links(url, user_agent=None, proxy=None):
    headers = {'User-Agent': user_agent} if user_agent else None
    proxies = {'http': proxy} if proxy else None
    response = requests.get(url, headers=headers, proxies=proxies)
    html = response.text
    soup = BeautifulSoup(html, 'lxml') 
    # page_pattern = re.compile('--list-item--')
    pages = soup.findAll(class_=page_pattern)

    links = [url]
    for page in pages:
        if page.a:
            link = page.a['href']
            if not re.match('https://www.cian.ru', link):
                link = 'https://www.cian.ru' + link
            links.append(link)

    if not pages or not pages[-1].a:
        return links
    else:
        next_links = get_links(links[-1])
        parsed_links = [parse_qs(link) for link in links]

        for link in next_links:
            if parse_qs(link) not in parsed_links:
                links.append(link)

    return links

@shared_task
def parse(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    pattern = re.compile('--info--')
    ads = soup.findAll(class_=pattern)

    data = []

    for ad in ads:
        subtitle_pattern = re.compile('--subtitle--')
        div = ad.find(class_=subtitle_pattern)

        if not div:
            no_subtitle_pattern = re.compile('--title--|--single_title-')
            div = ad.find(class_=no_subtitle_pattern)

        area = re.search('\d{2} м²', div.text)[0][:2]

        try:
            floor = re.search('\d+/\d+ этаж', div.text)[0][:-5]
        except TypeError:
            floor = '–'
        
        address_pattern = re.compile('--address-links--')
        address = ad.find(class_=address_pattern).span['content']
        
        price_pattern = re.compile('--header--')
        price = ad.find(class_=price_pattern, target='').text[:-7]

        apartment = Apartment(
            address=address, 
            total_area=area, 
            floor=floor,
            price=int(price.replace(' ', '')),
        )
        data.append(apartment)
        print(apartment)

    Apartment.objects.bulk_create(data)

@shared_task
def main():
    proxy = '212.42.104.74:3128'
    user_agent = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    links = get_links(URL, 
        user_agent=user_agent,
        proxy=proxy,
    )
    print('LINKS', links)

    job = group(parse.s(link) for link in links)
    job.apply_async()
    
# 212.42.104.74:3128
# 213.163.122.194:8080
# 213.163.122.197:8080
# 212.200.126.16:8080
# 212.33.28.53:8080
# 212.92.204.54:80
# 212.22.86.114:3130
# 212.129.5.248:54321
# 212.129.1.152:54321
# 13.233.195.181:80

# Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1
# Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0
# Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1
# Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0
# Mozilla/5.0 (X11; U; Linux Core i7-4980HQ; de; rv:32.0; compatible; JobboerseBot; http://www.jobboerse.com/bot.htm) Gecko/20100101 Firefox/38.0
# Mozilla/5.0 (Windows NT 5.1; rv:36.0) Gecko/20100101 Firefox/36.0
# Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0
# Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0
# Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0
# Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36
# Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36
# Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36
# Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
# Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36
# Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36
# Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36
# Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1
# Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36
# Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36