from codecs import encode
from datetime import datetime
import time
import json
import threading
from bs4 import BeautifulSoup
from send_email import send_email
import sys
from logger import  get_logger
from tracker import get_BasicTracker_by_name, get_DynamicTracker_by_name, BasicTracker


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

class Runner(threading.Thread):
  
  def __init__(self, tracker):
    super().__init__()
    self.tracker=tracker
    
  def run(self) -> None:
    self.tracker.run()
        
  
def argparser():
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument("-d", "--debug", action="store_true", dest="debug")
  args = parser.parse_args()
  return args.debug

default_config = {
    "extract_all":False,
    "email_messages":"內容已更新！",
    "encoding":False,
    "update_second":300,
    "mode":"Basic",
    "tracker":"BasicTracker"
    }

DEBUG=argparser()
with open('config.json','r') as f:
  track_website_infos=json.load(f)

  

if DEBUG:
  print("!!!!! DEBUG Mode !!!!!")

trackers=[]
for track_website_info in track_website_infos:
  website_info = dict(default_config)
  website_info.update(track_website_info)
  func_name=f'get_{website_info["mode"]}Tracker_by_name("{website_info["tracker"]}")'
  tracker = eval(func_name)
  trackers.append(Runner(tracker(website_info=website_info,
                                 debug = DEBUG,
                                 config_path='config.json')))
  trackers[-1].start()
  time.sleep(2)
for track_website_info in track_website_infos:
  for tracker in trackers:
    tracker.join()
    
