import time
import requests
from bs4 import BeautifulSoup
from send_email import send_email
from logger import  get_logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import threading
import sys
import pyuseragents
import collections 
import copy
def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d
  
class BasicTracker(threading.Thread):

  def get_default_config(self):
    return {
            "extract_all":False,
            "encoding":False,
            "update_second":300,
            "tracker":{
              "mode":"Basic",
              "tracker_name":"BasicTracker"
              }
          }
                        
  def __init__(self, website_info, config_path, debug=False):
    super().__init__()
    self.website_info = self.load_config(website_info)
    self.tracker_info = self.website_info['tracker']
    self.logger = get_logger(self.website_info['website_name'])
    self.debug = debug
    self.config_path = config_path
    self.destroy = False
    self.name = self.website_info['website_name']
    
  def get_header(self):
    HEADERS = {
            "User-Agent": pyuseragents.random(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            # "Accept-Language": "en-US,en-GB,zh-cn; q=0.5",
            "referer": "https://shopee.tw/",
            "Accept-Encoding": "br, gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded; application/json; charset=UTF-8",
            "Connection": "keep-alive"
        }
    return HEADERS
    
  def close(self): 
    self.destroy=True
    self.logger.info(f'【Closing 【{self.name}】 tracker】')
    
  def load_config(self, website_info):
    _website_info = copy.deepcopy(dict(self.get_default_config()))
    update_dict(_website_info,website_info)
    return _website_info

  def update_config(self):
    with open(self.config_path,'r') as f:
      track_website_infos=json.load(f)
    
    for track_website_info in track_website_infos:
      if track_website_info['website_name'] == self.website_info['website_name']:
        new_website_info = self.load_config(track_website_info)
        if self.website_info!=new_website_info:
          self.website_info = dict(new_website_info)
          self.tracker_info = self.website_info['tracker']
          self.logger.info('【Config Updated】')
          self.log_config()
          print('')
        
  def log_config(self):
    for k,v in self.website_info.items():
      self.logger.debug(f'{k}: {v}')
    
  def init_tracker(self):
    self.annotations = self.get_annotation()
    while self.annotations is None:
      self.logger.info(f'Initialize {self.name} Tracker Error')
      self.logger.info(f'Re-initialize again after {self.website_info["update_second"]} second.....')
      self.annotations = self.get_annotation()
      time.sleep(self.website_info["update_second"])
      
    self.logger.debug('【Initialize Config】')
    self.log_config()
    self.logger.debug('Init annotations:\n'+ str(self.annotations))   
    
    self.logger.info('【Initialize Website Tracker】')
    self.logger.info('Website: '+self.website_info["website_name"])
    self.logger.info('Link: '+self.website_info["target_URL"])
    self.logger.info('Emails: '+str(self.website_info["to_emails"]))
    self.logger.info('Update Frequency: '+str(self.website_info["update_second"])+ ' second')

    print('')
    
  def get_page_content(self):
    try:
      response = requests.get(self.website_info["target_URL"],headers = self.get_header())
      if self.website_info["encoding"]:
          response.encoding = self.website_info["encoding"]

      if response.status_code != 200:
        self.logger.warning("State Code: "+str(response.status_code))
        return None
      
    except Exception as e:
      self.logger.error("Error message: "+ str(e))
      return None
    
    return response.text

  def extract_annotation(self, page_content):
      soup = BeautifulSoup(page_content, "html.parser")
      find_element_info = self.website_info['find_element']
      # extract all element
      if self.website_info['extract_all']:
        if 'id' in find_element_info.keys():
          # annotations = [ i.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','') for i in soup.find_all(find_element_info["tag"],id=find_element_info["id"])]   
          annotations = [ i.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','') for i in soup.find_all(find_element_info["tag"],id=find_element_info["id"])]   
        else:
          annotations = [ i.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','') for i in soup.find_all(find_element_info["tag"],class_=find_element_info["class_name"])]
        
        if annotations is None:
          self.logger.warning(f'Annotations find element return None')
          self.logger.warning(f'Tag and id or class_name: {self.website_info["find_element"]}')
          print('')
          return None
    
        annotations = '\n'.join(annotations)
      
      else:
        if 'id' in find_element_info.keys():
          annotations = soup.find(find_element_info["tag"],id=find_element_info["id"])
        else:
          annotations = soup.find(find_element_info["tag"],class_=find_element_info["class_name"])
        if annotations is None:
          self.logger.warning('Annotations find element return None')
          self.logger.warning(f'Tag and id or class_name: {self.website_info["find_element"]}')
          print('')
          return None
        annotations = annotations.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','')
      return annotations
    
  def post_process(self,annotations):
    if 'filtering' in self.website_info.keys():
      if isinstance(self.website_info['filtering'],list):
        for word in self.website_info['filtering']:
          annotations = annotations.replace(word,'')
      else:
        annotations = annotations.replace(word,'')
    return annotations.strip()

  def final_process(self,annotations):
    return annotations
  
  def get_annotation(self):
      page_content = self.get_page_content()
      if page_content == None:
        return None
      
      with open(f'extract_html/{self.name}.html','w') as f:
        f.write(page_content)
        
      new_annotations = self.extract_annotation(page_content)
      
      if new_annotations == None:
        return None
      
      if self.debug:
        print(f'extract annotation:\n{new_annotations}')
        
      new_annotations = self.post_process(new_annotations)
      new_annotations = self.final_process(new_annotations)
      
      if self.debug:
        print(f'post process annotation:\n{new_annotations}')
        
      return new_annotations
    
  def checking(self,new_annotations):
    return self.annotations!=new_annotations

  def _send_email(self, new_annotations):
    email_content='Website: {website_name}\n Link: {link}\n\n {message} \n\n====Original====\n {original}\n=====Update=====\n{update}'
    send_email(content_text = email_content.format(website_name=self.website_info["website_name"],
                                                    link=self.website_info["target_URL"],
                                                    message=self.website_info["email_messages"],
                                                    original=self.annotations,
                                                    update=new_annotations),
                                                    to_email =self.website_info["to_emails"]
                                                  )

  def send_email(self,new_annotations):
    self.logger.info(f'============== Website 【{self.website_info["website_name"]}】 Update! ==============')
    self.logger.info('Link: '+self.website_info["target_URL"])
    self.logger.info('New Annotations:\n'+ str(self.annotations))
    self.logger.info('Emails: '+str(self.website_info["to_emails"]))
    self.logger.info('Remind Message: '+self.website_info["email_messages"])
    self.logger.info('Send Email ...')
    
    if not self.debug:
      self._send_email(new_annotations)
      print('')

  def run(self):
    self.init_tracker()
    
    while(True):
      self.update_config()    
      time.sleep(self.website_info["update_second"])

      if self.destroy:
        return
      
      new_annotations = self.get_annotation()
      
      if new_annotations == None:
        continue
      
      if self.checking(new_annotations):
        self.send_email(new_annotations) 
        self.annotations = new_annotations
        
        
class DynamicTracker(BasicTracker):
  def get_default_config(self):
    return {
            "extract_all":False,
            "encoding":False,
            "update_second":300,
            "tracker":{
              "mode":"Dynamic",
              "tracker_name":"BasicTracker",
              "dynamic_delay": 6,
              "scorll_times": 3,
              }
           }

  def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
  def init_driver(self):
      options = Options()
      options.add_argument('--headless')
      options.add_argument('--no-sandbox')
      options.add_argument('--disable-dev-shm-usage')
      options.add_argument('--disable-notifications')
      options.add_argument('--user-agent=%s' % pyuseragents.random())
      options.add_argument('--accept=%s' % "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
      options.add_argument('--accept-encoding=%s' % "br, gzip, deflate")
      options.add_argument('--content-type=%s' % "application/x-www-form-urlencoded; application/json; charset=UTF-8")
      options.add_argument('--Connection=%s' % "keep-alive")
      self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
      
  def get_page_content(self):
    self.init_driver()
    try:
      self.driver.get(self.website_info["target_URL"])
      time.sleep(self.tracker_info['dynamic_delay'])
      scroll_times = self.tracker_info['scorll_times']
      for i in range(scroll_times):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(self.tracker_info['dynamic_delay'])
        # self.driver.implicitly_wait(self.tracker_info['dynamic_delay'])

      page_content = self.driver.page_source
      self.driver.close()
      
    except Exception as e:
      self.driver.close()
      self.logger.error("Error message: "+ str(e))
      print('')
      return None
    return page_content
  
  
def get_BasicTracker(basic_tracker):
  if basic_tracker is DynamicTracker:
    return get_DynamicTracker(BasicTracker)
  return BasicTracker

def get_DynamicTracker(basic_tracker):
  return DynamicTracker