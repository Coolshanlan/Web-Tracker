from codecs import encode
from datetime import datetime
import time
import json
import threading
from bs4 import BeautifulSoup
from send_email import send_email
import sys
from logger import  get_logger
from tracker import *


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


DEBUG=argparser()
with open('config.json','r') as f:
  track_website_infos=json.load(f)
  

if DEBUG:
  print("!!!!! DEBUG Mode !!!!!")

trackers=[]
for track_website_info in track_website_infos:
  tracker = eval(track_website_info['Tracker'])
  trackers.append(Runner(tracker(website_info=track_website_info,
                                 debug = DEBUG)))
  trackers[-1].start()
  time.sleep(1)
  
for track_website_info in track_website_infos:
  trackers[-1].join()
    
