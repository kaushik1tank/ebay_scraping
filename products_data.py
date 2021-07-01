from bs4 import BeautifulSoup
import json
from time import sleep
import datetime
from unidecode import unidecode
import requests
import datetime
import pandas as pd

products = []
er = []

def whitespace(val):
    whitespace = ('\t','\n','\r','\v','\f','   ','  ')
    for wh in whitespace:
        val = val.replace(wh, '')
    
    val = unidecode(val)
    return val


def get_product_p(bs):
    print('trying to get data')

    # title
    title = bs.find('h1', attrs={'class':'product-title'}).text
    title = whitespace(title)

    # Specifications
    spec = bs.find('section', attrs={'class':'product-spectification'}).find_all('div', attrs={'class':'spec-row'})

    # escription
    desc = ''
    try:
        if 'Product Information' in (spec[0].find('h2').text):
            desc = spec[0].find('ul').text
            desc = whitespace(desc)
            spc = bs.find('section', attrs={'class':'product-spectification'}).find_all('li')
            del(spc[0])
        else:
            desc = ''
            spc = bs.find('section', attrs={'class':'product-spectification'}).find_all('li')


    except:
        desc = ''
        spc = bs.find('section', attrs={'class':'product-spectification'}).find_all('li')

    # Item Specificaions
    sp_dic = {}
    prod_number = ''
    brand = ''
    prod_weight = ''
    prod_size = ''
    for sp in spc:
        key = sp.find('div', attrs={'class':'s-name'}).text
        key = whitespace(key)
        val = sp.find('div', attrs={'class':'s-value'}).text
        val = whitespace(val)
        if 'eBay Product ID' in key:
            prod_number = val
        
        if key == 'Brand':
            brand = val

        if 'Item Weight' in key:
            prod_weight = val
        
        sp_dic[key] = val

    # Item size
    for sp in spec:
        try:
            if 'Dimensions' in sp.find('h2').text:
                for li in sp.find_all('li'):
                    v1 = li.find('div', attrs={'class':'s-name'}).text
                    v2 = li.find('div', attrs={'class':'s-value'}).text
                    prod_size = prod_size + v1 +': '+ v2 + ' , '
                    
                prod_size = whitespace(prod_size)
            
            else:
                prod_size = ''
        except:
            None
            
    # price
    price = bs.find('div', attrs={'class':'display-price'}).text.replace('$','')

    # Ratings and reviews
    try:
        ratings = bs.find('span', attrs={'class':'review--start--rating'}).text
        reviews = bs.find('span', attrs={'class':'reviews--count'}).text.replace(' product ratings','').replace('average based on ','').replace(' rating','')
    except:
        ratings = ''
        reviews = ''

    # Seller info
    seller_name = bs.find('div', attrs={'class':'seller-details'}).find_all('span', attrs={'class':'no-wrap'})[1].text

    # return policy
    ret = bs.find_all('ul', attrs={'class':'item-highlights'})[1].find_all('li', attrs={'class':'item-highlight'})
    for re in ret:
        if 'returns' in re.text:
            returns = re.text
            returns = whitespace(returns)
    
    # images
    img = bs.find_all('div', attrs={'class':'app-filmstrip__owl-carousel'})[0].find_all('img')
    imgs = ''
    print(len(img))
    for im in img:
        image = im['data-originalimg']
        imgs = imgs + image + ' , '
        

    # timestamp
    tim = datetime.datetime.now()
    timestamp = tim.strftime('%m/%d/%Y %H:%M:%S %p')

    # discounts in percentage
    try:
        discount_perc = bs.find('div', attrs={'id':'center-panel'}).find('span', attrs={'class':'cc-ts-EMPHASIS cc-ts-BOLD'}).text.replace('Save ','')
    except:
        discount_perc = ''

    # offers
    try:
        offer = bs.find('div', attrs={'class':'item-desc'}).find('div', attrs={'class':'item-offer-row dual-format'}).find('div', attrs={'class':'item-content-wrapper'}).text
        offer = whitespace(offer)
    except:
        offer = ''

    d = {}
    d['Domain'] = 'https://www.ebay.com/'
    d['Timestamp'] = timestamp
    d['Product Name(Title)'] = title
    d['Product Unique Number'] = prod_number
    d['Product Category'] = 'Books, Movies & Music'
    d['Product Subcategory'] = 'Musical Instruments & Gear'
    d['Product Brand'] = brand
    d['Product Specification'] = sp_dic
    d['Product Details'] = desc
    d['Price'] = price
    d['No. Of Ratings'] = ratings
    d['No. Of Reviews'] = reviews
    d['Product Size'] = prod_size
    d['Product Weight'] = prod_weight
    d['Best Seller Rank'] = ''
    d['Product Unit'] = ''
    d['Tier 1 Price'] = ''
    d['Tier 1 Units'] = ''
    d['Tier 2 Price'] = ''
    d['Tier 2 Units'] = ''
    d['Offers'] = offer
    d['Seller Name'] = seller_name
    d['Return Policy'] = returns
    d['Product Images Url'] = imgs
    d['Country'] = 'US'
    d['Product Url'] = url
    d['Type Of Website'] = 'b2c'
    d['Discount In Percent'] = discount_perc
    d['Discount In USD'] = ''

    print('saving')
    products.append(d)
    with open('' 'a') as f:
        f.write(json.dumps(d))



x = open('', 'r')
jsn_urls = json.load(x)
x.close()

for u in jsn_urls:
    url = u['url']
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

    retry = 0
    response = ""
    while retry < 5:
        response =  requests.request("POST",main_url,headers=headers,data=payload).text
        
        if '#add_identiflyer_name' in response:
            break

        else:
            response = ""
            retry += 1    
            print("===========",retry,"=======================")

    bs = BeautifulSoup(response,'lxml')

    # if the page url has /p/ in url
    if '/p/' in url:
        get_product_p(bs)

    else:
        get_product_itm(bs)
