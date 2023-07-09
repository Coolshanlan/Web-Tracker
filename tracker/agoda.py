
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests
import logging
from .basic_tracker import BasicTracker

class AgodaTracker(BasicTracker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def init_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-notifications")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver = driver
        
    def extract_feature(self, soup):
        annotations = soup.find(self.website_info["tag"],class_=self.website_info["class_name"])
        annotations = annotations.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','')
        annotations = int(annotations.split("NT$ ")[-1].replace(',',''))
        return annotations

    def get_annotation(self):
        self.init_driver()
        try:
            self.driver.get(self.website_info["target_URL"])
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(5)
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(5)
            page_source=self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            self.driver.close()
            self.annotations = self.extract_feature(soup)

        except Exception as e:
            self.logger.error("Error message: "+ str(e))
            return None
        
        return self.annotations

    def checking(self,new_annotations):
        return (self.annotations-new_annotations) > int(self.website_info['update_diff'])
 

