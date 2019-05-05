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

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Schedule.settings")
# django.setup()
from .models import Apartment


URL = 'https://www.cian.ru/cat.php?deal_type=rent&engine_version=2&maxarea=30&minarea=20&offer_type=flat&region=1&room1=1&type=4'

def get_links(url, user_agent=None, proxy=None):
    headers = {'User-Agent': user_agent} if user_agent else None
    proxies = {'http': proxy} if proxy else None
    response = requests.get(url, headers=headers, proxies=proxies)
    html = response.text
    soup = BeautifulSoup(html, 'lxml') 
    page_pattern = re.compile('--list-item--')
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
    links = get_links(URL)
    job = group(parse.s(link) for link in links)
    job.apply_async()
