from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import schedule
import time


def check_flights():
    url = "https://www.google.com/flights/explore/#explore;f=OSL,TRF,RYG;t=r-England,+United+Kingdom-0x47d0a98a6c1ed5df%253A0xf4e19525332d8ea8;li=3;lx=5;d=2018-01-24"
    driver = webdriver.PhantomJS()
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36")
    driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-error=true'])
    driver.implicitly_wait(20)
    driver.get(url)

    wait =WebDriverWait(driver, 20)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"span.CTPFVNB-v-c")))

    s = BeautifulSoup(driver.page_source, "lxml")

    best_price_tags = s.findAll('div', 'CTPFVNB-w-d')


check_flights()
