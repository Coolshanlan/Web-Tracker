from __future__ import annotations
from codecs import encode
from datetime import datetime
import time
import json
import requests
import threading
from bs4 import BeautifulSoup
from send_email import send_email
import sys
from logger import  get_logger
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

class Tracker(threading.Thread):
  
  def __init__(self, track_website_info):
    super().__init__()
    self.track_website_info=track_website_info
    
  def run(self) -> None:
    track_func(**self.track_website_info)

def extract_feature(soup,tag,class_name):
    annotations = [ i.text.replace('\xa0','').replace('\n','|').replace('||||','|').replace('|||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('||','|').replace('|','\n').replace('\r','').replace('\t','') for i in soup.find_all(tag,class_=class_name)]
    annotations = '\n'.join(annotations)
    return annotations


def update(target_URL,feature_f,tag,class_name,encoding=None):
  try:
    response = requests.get(target_URL)
    if encoding:
        response.encoding = encoding

    if response.status_code != 200:
      return None
    soup = BeautifulSoup(response.text, "html.parser")
    annotations = feature_f(soup,tag,class_name)

  except Exception as e:
    print("Error message: ", e)
    return None
  return annotations


def track_func(target_URLs,tag,class_name,encodings,website_names,email_messages,to_emails,update_second,extract_feature=extract_feature):
  annotations = update(target_URLs,extract_feature,tag,class_name,encodings)
  logger.info('============== Initialize Website Tracker ===============')
  logger.info('Website: '+website_names)
  logger.info('Link: '+target_URLs)
  logger.info('Emails: '+str(to_emails))
  logger.info('Remind Message: '+email_messages)
  logger.info('Update Frequency: '+str(update_second)+ ' second')
  logger.debug('Init annotations: '+annotations)
  
  while(True):
    time.sleep(update_second)
    new_annotations = update(target_URLs,extract_feature,tag,class_name,encodings)
    if new_annotations == None:
      continue
    if annotations!=new_annotations:
      logger.info(f'============== Website 【{website_names}】 Update! ===============')
      logger.info('Link: '+target_URLs)
      logger.info('New Annotations: '+new_annotations)
      logger.info('Emails: '+str(to_emails))
      logger.info('Remind Message: '+email_messages)
      logger.info('Send Email ...')
      annotations = new_annotations
      
      if not DEBUG:
        send_email(content_text = 'Website: '+website_names+'\n Link: '+target_URLs+'\n\n'+email_messages+'\n Update: '+new_annotations, to_email =to_emails)
      
      
  
def argparser():
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument("-d", "--debug", action="store_true", dest="debug")
  args = parser.parse_args()
  return args.debug


DEBUG=argparser()
logger = get_logger('record_log')

with open('config.json','r') as f:
  track_website_infos=json.load(f)
  

if DEBUG:
  logger.info("!!!!! DEBUG Mode !!!!!")

trackers=[]
for track_website_info in track_website_infos:
  trackers.append(Tracker(track_website_info))
  trackers[-1].start()
  time.sleep(1)
  
for track_website_info in track_website_infos:
  trackers[-1].join()
    
