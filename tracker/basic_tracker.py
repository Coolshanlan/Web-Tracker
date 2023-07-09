import time
import requests
from bs4 import BeautifulSoup
from send_email import send_email
from logger import  get_logger

class BasicTracker():
  def __init__(self, website_info, debug=False):
    self.website_info = website_info
    self.logger = get_logger(self.website_info['website_name'])
    self.debug = debug

    
  def init_tracker(self):
    self.annotations = self.get_annotation()
    self.logger.debug('============== Config ==============')
    for k,v in self.website_info.items():
      self.logger.debug(f'{k}: {v}')
    self.logger.debug('Init annotations: '+ str(self.annotations))

    self.logger.info('============== Initialize Website Tracker ===============')
    self.logger.info('Website: '+self.website_info["website_name"])
    self.logger.info('Link: '+self.website_info["target_URL"])
    self.logger.info('Emails: '+str(self.website_info["to_emails"]))
    # self.logger.info('Remind Message: '+self.website_info["email_messages"])
    self.logger.info('Update Frequency: '+str(self.website_info["update_second"])+ ' second')
    
  def extract_feature(self, soup):
      annotations = [ i.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','') for i in soup.find_all(self.website_info["tag"],class_=self.website_info["class_name"])]
      annotations = '\n'.join(annotations)
      return annotations


  def get_annotation(self):
    try:
      response = requests.get(self.website_info["target_URL"])
      if self.website_info["encoding"]:
          response.encoding = self.website_info["encoding"]

      if response.status_code != 200:
        self.logger.warning("State Code: "+str(response.status_code))
        return None
      soup = BeautifulSoup(response.text, "html.parser")
      self.annotations = self.extract_feature(soup)

    except Exception as e:
      self.logger.error("Error message: "+ str(e))
      return None
    return self.annotations

  def checking(self,new_annotations):
    return self.annotations!=new_annotations

  def run(self):
    self.init_tracker()
    
    while(True):
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
        