import sys
import requests

import pandas as pd
import numpy as np

import schedule
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from bs4 import BeautifulSoup

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


def check_flights():
    url = "https://www.google.com/flights/explore/#explore;f=OSL,TRF,RYG;t=r-England," \
          "+United+Kingdom-0x47d0a98a6c1ed5df%253A0xf4e19525332d8ea8;li=3;lx=5;d=2018-01-28"
    service = webdriver.chrome.service.Service('C:\Program Files\chromedriver\chromedriver.exe')
    service.start()
    capabilities = {'chrome.binary': 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'}
    driver = webdriver.Remote(service.service_url, capabilities)
    driver.get(url)
    time.sleep(10)

    wait = WebDriverWait(driver, 20)
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "span.CTPFVNB-v-c")))

    s = BeautifulSoup(driver.page_source, "lxml")

    best_price_tags = s.findAll('div', 'CTPFVNB-w-e')

    # see if it worked
    if len(best_price_tags) < 4:
        print('Failed to Load Page Data')
        requests.post('https://maker.ifttt.com/trigger/fare_alert/with/key/bkSYqcLcxdVIqDUjWo1W20',
                      data={"value1": "script", "value2": "failed", "value3": ""})
        sys.exit(0)
    else:
        print('Successfully Loaded Page Data')

    best_prices = []
    for tag in best_price_tags:
        best_prices.append(int(tag.text.replace('$', '').replace(',', '')))

    best_price = best_prices[0]

    best_height_tags = s.findAll('div', 'CTPFVNB-w-x')
    best_heights = []
    for t in best_height_tags:
        best_heights.append(float(t.attrs['style'].split('height:')[1].replace('px;', '')))

    best_height = best_heights[0]

    # Price per pixel of height
    pph = np.array(best_price) / np.array(best_height)

    cities = s.findAll('div', 'CTPFVNB-w-o')

    hlist = []
    for bar in cities[0] \
            .findAll('div', 'CTPFVNB-w-x'):
        hlist.append(float(bar['style'].split('height:')[1].replace('px;', '')) * pph)

    fares = pd.DataFrame(hlist, columns=['price'])
    px = [x for x in fares['price']]
    ff = pd.DataFrame(px, columns=['fare']).reset_index()

    x = StandardScaler().fit_transform(ff)
    db = DBSCAN(eps=.5, min_samples=1).fit(x)

    labels = db.labels_
    clusters = len(set(labels))

    pf = pd.concat([ff, pd.DataFrame(db.labels_, columns=['cluster'])], axis=1)
    rf = pf.groupby('cluster')['fare']\
        .agg(['min', 'count']).sort_values('min', ascending=True)

    if clusters > 1 \
            and ff['fare'].min() == rf.iloc[0]['min'] \
            and rf.iloc[0]['count'] < rf['count'].quantile(.10) \
            and rf.iloc[0]['fare'] + 100 < rf.iloc[1]['fare']:
            city = s.find('span', 'CTPFVNB-v-c').text
            fare = s.find('div', 'CTPFVNB-w-e').text
            requests.post('https://maker.ifttt.com/trigger/fare_alert/with/key/bkSYqcLcxdVIqDUjWo1W20',
                          data={"value1": city, "value2": fare, "value3": ""})
    else:
        print('no alert triggered')


print("Successfully Built")

schedule.every(30).minutes.do(check_flights)

while 1:
    schedule.run_pending()
    time.sleep(1)
