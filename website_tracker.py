from codecs import encode
from datetime import datetime
import time
import json
import threading
from bs4 import BeautifulSoup
from send_email import send_email
import sys
from logger import get_logger
from tracker import get_Tracker
import collections
import copy
from utils import *


def argparser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", dest="debug")
    parser.add_argument("-t", "--test", default=None,
                        dest="test_index", type=int)
    args = parser.parse_args()
    return args

def create_tracker_runner(website_info):
    website_info = load_info(website_info)
    tracker_info = website_info['tracker']
    tracker = get_Tracker(tracker_info["tracker_name"], tracker_info["mode"])
    return tracker(website_info=website_info,
                   debug=DEBUG,
                   config_path='config.json')

# -------------- main --------------
track_website_infos = load_config()
args = argparser()
DEBUG = args.debug
TEST_INDEX = args.test_index

if DEBUG or TEST_INDEX is not None:
    DEBUG = True
    print("!!!!! DEBUG Mode !!!!!")

    if TEST_INDEX is not None:
        website_info = track_website_infos[TEST_INDEX]
        runner = create_tracker_runner(website_info)
        runner.start()
        time.sleep(60)
        runner.close()
        exit()


trackers = {}
for track_website_info in track_website_infos:
    if track_website_info['enable']:
        tracker_runner = create_tracker_runner(track_website_info)
        trackers[track_website_info['website_name']] = tracker_runner
        trackers[track_website_info['website_name']].start()
        time.sleep(2)

while True:
    time.sleep(60)
    track_website_infos = load_config()
    if track_website_infos is None:
        continue
    for track_website_info in track_website_infos:
        if track_website_info['enable'] and track_website_info['website_name'] not in trackers:
            tracker_runner = create_tracker_runner(track_website_info)
            trackers[track_website_info['website_name']] = tracker_runner
            trackers[track_website_info['website_name']].start()
            time.sleep(2)
        elif track_website_info['enable'] == False and track_website_info['website_name'] in trackers:
            trackers[track_website_info['website_name']].close()
            del trackers[track_website_info['website_name']]

    if len(trackers.keys()) == 0:
        break
