
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests
import logging
from .basic_tracker import DynamicTracker, BasicTracker
from send_email import send_email

def get_NumberTracker(basic_tracker):
    class NumberTracker(basic_tracker):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.achieved =False
            self.last_annotation=None
            
        def final_process(self,annotations):
            return float(annotations)
            
        def checking(self,new_annotations):
            if self.last_annotation is None:
                self.last_annotation = new_annotations
            
            # record history
            if self.last_annotation != new_annotations:
                self.last_annotation = new_annotations
                self.logger.debug(f'Annotation update record:{new_annotations}')
            
            # check if number achieve the target number    
            target_info = self.tracker_info["target_number"]
            
            # keep tracking
            if 'number' in target_info.keys() and not self.achieved:
                self.achieved = (new_annotations >= target_info['number']) if target_info['mode'] == "bigger" else (new_annotations < target_info['number'])
                return self.achieved

            if "remind_diff" in target_info.keys():
                if target_info['mode'] == 'bigger':
                    return (new_annotations-self.annotations) >= int(target_info['remind_diff'])
                else:
                    return (new_annotations-self.annotations) <= int(target_info['remind_diff'])
            # destroy runner
            else: # no remind_diff and achieved
                self.destroy=True
                return False        
        
    return NumberTracker


def get_ListNewTracker(basic_tracker):
    class ListNewTracker(basic_tracker):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.achieved =False
            self.last_annotation=None
        
            
        def checking(self,new_annotations):
            if self.last_annotation is None:
                self.last_annotation = new_annotations
            
            if len(set(new_annotations.split('\n'))-set(self.annotations.split('\n') ))>0:
                return True
            elif self.last_annotation != new_annotations:
                self.last_annotation = new_annotations
                self.logger.debug(f'Annotation update record:\n{new_annotations}')
            return False
        
        def send_email(self,new_annotations):
            new_annotations = '\n'.join(list(set(new_annotations.split('\n'))-set(self.annotations.split('\n') )))
            self.logger.info(f'============== Website 【{self.website_info["website_name"]}】 Update! ==============')
            self.logger.info('Link: '+self.website_info["target_URL"])
            self.logger.info('New Annotations:\n'+ str(new_annotations))
            self.logger.info('Emails: '+str(self.website_info["to_emails"]))
            self.logger.info('Remind Message: '+self.website_info["email_messages"])
            self.logger.info('Send Email ...')
            
            if not self.debug:
                self._send_email(new_annotations)
                print('')

    return ListNewTracker
