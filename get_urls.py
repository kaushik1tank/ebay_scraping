from random import randint
from time import sleep
from unidecode import unidecode
from bs4 import BeautifulSoup
from random import randint
from fake_headers import Headers

import pandas as pd
import json
import csv
import requests

# open categories files to get sub categories urls 
x = open('/content/drive/MyDrive/Colab Notebooks/eCommerce/ebay/All Categories/Collectibles & Art/Collectibles & Art2.json', 'r')
jsn_url = json.load(x)
x.close()
len(jsn_url)

# save all errors urls in er
er = []

# to get data from page source 
def get_urls(all_itm):
    for itm in all_itm:
        url = itm.find('a')['href']
        title = itm.find('h3').text

        d = {}
        d['title'] = unidecode(title)
        d['url'] = url

        # save all urls into the list 
        urls.append(d)

        # save each individual url into file for avoding erros during runtime 
        with open('/content/drive/MyDrive/Colab Notebooks/eCommerce/ebay/All Categories/Collectibles & Art/urls2.json', 'a') as f:
            f.write(json.dumps(d))



for x in jsn_url:
    fname = '/content/drive/MyDrive/Colab Notebooks/eCommerce/ebay/All Categories/Collectibles & Art/' + x['name'] + '.json'
    urls = []
    print('loading category', x['name'])
    for num in range(1, len(x['sub_cat'])):
        y = x['sub_cat'][num]
        try:
            url = y['url']
            print('loading: ', url)

            # implemented worker 
            main_url = "https://rentech.genericapi.workers.dev"

            payload = json.dumps({
            "url": url,
            "options": {
                "method": "GET",
                "headers": {
                    "content-type": "text/html;charset=UTF-8",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                }
            }
            })
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", main_url, headers=headers, data=payload)
            bs = BeautifulSoup(response.content, 'lxml')

            # get all the itms from page
            all_itm = bs.find('ul', attrs={'class':'b-list__items_nofooter'}).find_all('li')

            get_urls(all_itm)
            pre_url = url

            # from 2nd page to the last page of sub categores
            next_page = bs.find('a', attrs={'rel':'next'})['href']
            if '#' in next_page:
                print('rich at the end')
                next_page = ''
            else:
                while(next_page):
                    print(len(urls))
                    print(urls[-1:][0]['title'])
                    print('loading page: ', next_page)
                    
                    # implemented worker
                    payload = json.dumps({
                    "url": next_page,
                    "options": {
                        "method": "GET",
                        "headers": {
                            "content-type": "text/html;charset=UTF-8",
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                        }
                    }
                    })
                    headers = {
                    'Content-Type': 'application/json'
                    }

                    retry = 0
                    response = ""
                    while retry < 5:
                        response =  requests.request("POST",main_url,headers=headers,data=payload).text
                        
                        if 'class="b-list__items_nofooter' in response:
                            break

                        else:
                            response = ""
                            retry += 1    
                            print("===========",retry,"=======================")            


                    sleep(.1)
                    bs = BeautifulSoup(response,'lxml')
                    all_itm = bs.find('ul', attrs={'class':'b-list__items_nofooter'}).find_all('li')
                    get_urls(all_itm)
                    try:
                        pre_url = next_page
                        next_page = ''
                        next_page = bs.find('a', attrs={'rel':'next'})['href']
                        if '#' in next_page:
                            print('rich at the end')
                            next_page = ''
                        else:
                            continue
                    except:
                        print('erroe with finding next page')
        except:
            erd = {}
            erd['name'] = y['name']
            erd['next_page'] = next_page
            er.append(erd)
            print(erd)

    # save file for each sub categories to identify sub categories
    with open(fname, 'a') as f:
        f.write(json.dumps(urls))
        
    print('File saved for category: ', x['name'])
    print('total scraped urls are: ', len(all_urls))
