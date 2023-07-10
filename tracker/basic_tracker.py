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

class BasicTracker():
  default_config={
    "target_URL":"https://tokyosharehouse.com/jpn/house/room/2933/empty/",
    "tag":"div",
    "class_name":"content-room",
    "extract_all":False,
    "website_name":"日本女性專屬外宿網站",
    "email_messages":"空屋房間已更新！",
    "to_emails":["joey0201020123@gmail.com"],
    "encoding":False,
    "update_second":300,
    "mode":"Basic",
    "tracker":"BasicTracker"
    }
  
  def __init__(self, website_info, config_path, debug=False):
    self.website_info = self.load_config(website_info)
    self.logger = get_logger(self.website_info['website_name'])
    self.debug = debug
    self.config_path = config_path
    self.destroy = False
    
  def load_config(self, website_info):
    _website_info = dict(BasicTracker.default_config)
    _website_info.update(website_info)
    return _website_info

  def update_config(self):
    with open(self.config_path,'r') as f:
      track_website_infos=json.load(f)
    
    for track_website_info in track_website_infos:
      if track_website_info['website_name'] == self.website_info['website_name']:
        new_website_info = self.load_config(track_website_info)
        if self.website_info!=new_website_info:
          self.website_info = dict(new_website_info)
          self.logger.info('==============Config Updated ==============')
          self.log_config()
        
  def log_config(self):
    for k,v in self.website_info.items():
      self.logger.debug(f'{k}: {v}')
    
  def init_tracker(self):
    self.logger.debug('============== Initialize Config ===============')
    self.log_config()
    
    self.annotations = self.get_annotation()
    self.logger.debug('Init annotations: '+ str(self.annotations))   
    
    self.logger.info('============== Initialize Website Tracker ===============')
    self.logger.info('Website: '+self.website_info["website_name"])
    self.logger.info('Link: '+self.website_info["target_URL"])
    self.logger.info('Emails: '+str(self.website_info["to_emails"]))
    # self.logger.info('Remind Message: '+self.website_info["email_messages"])
    self.logger.info('Update Frequency: '+str(self.website_info["update_second"])+ ' second')
  
  def get_page_content(self):
    try:
      response = requests.get(self.website_info["target_URL"])
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
      if self.website_info['extract_all']:
        annotations = [ i.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','') for i in soup.find_all(self.website_info["tag"],class_=self.website_info["class_name"])]
        annotations = '\n'.join(annotations)
      else:
        annotations = soup.find(self.website_info["tag"],class_=self.website_info["class_name"])
        annotations = annotations.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','')
      return annotations
    
  def post_process(self,annotations):
    if 'remove_word' in self.website_info.keys():
      if isinstance(self.website_info['remove_word'],list):
        for word in self.website_info['remove_word']:
          annotations = annotations.replace(word,'')
      else:
        annotations = annotations.replace(word,'')
    return annotations
  
  def get_annotation(self):
      page_content = self.get_page_content()
      if page_content == None:
        return None
      
      new_annotations = self.extract_annotation(page_content)
      if self.debug:
        print(f'extract annotation: {new_annotations}')
        
      new_annotations = self.post_process(new_annotations)
      if self.debug:
        print(f'post process annotation: {new_annotations}')
        
      return new_annotations
    
  def checking(self,new_annotations):
    return self.annotations!=new_annotations

  def run(self):
    self.init_tracker()
    
    while(True):
      if self.destroy: return 
      self.update_config()
      time.sleep(self.website_info["update_second"])
      
      new_annotations = self.get_annotation()
      
      if new_annotations == None:
        continue
      
      if self.checking(new_annotations):
        self.logger.info(f'============== Website 【{self.website_info["website_name"]}】 Update! ===============')
        self.logger.info('Link: '+self.website_info["target_URL"])
        self.logger.info('New Annotations: '+ str(self.annotations))
        self.logger.info('Emails: '+str(self.website_info["to_emails"]))
        self.logger.info('Remind Message: '+self.website_info["email_messages"])
        self.logger.info('Send Email ...')
        
        if not self.debug:
          email_content='Website: {website_name}\n Link: {link}\n\n {message} \n\n====Original====\n: {original}\n=====Update=====\n{update}'
          send_email(content_text = email_content.format(website_name=self.website_info["website_name"],
                                                         link=self.website_info["target_URL"],
                                                         message=self.website_info["email_messages"],
                                                         original=self.annotations,
                                                         update=new_annotations),
                     to_email =self.website_info["to_emails"])
          
        self.annotations = new_annotations
        
        
class DynamicTracker(BasicTracker):
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
      
      
  def get_page_content(self):
    self.init_driver()
    try:
      self.driver.get(self.website_info["target_URL"])
      self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
      time.sleep(5)
      self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
      time.sleep(5)
      page_content = self.driver.page_source
      self.driver.close()
      
    except Exception as e:
      self.driver.close()
      self.logger.error("Error message: "+ str(e))
      return None

    return page_content
  
  
def get_BasicTracker(basic_tracker):
  return BasicTracker

def get_DynamicTracker(basic_tracker):
  return DynamicTracker