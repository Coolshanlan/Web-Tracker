
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
            if "target_number" in self.tracker_info.keys():
                target_info=self.tracker_info["target_number"]
                
                # keep tracking
                if self.achieved and "remind_diff" in self.target_info.keys():
                    return (new_annotations-self.annotations) >= int(self.target_info['remind_diff'])
                # destroy runner
                elif self.achieved:
                    self.destroy=True
                    return False
                
                self.achieved = new_annotations >= target_info['number'] if target_info['mode'] == "bigger" else new_annotations < target_info['number']
                return self.achieved
            
            # Only remind diff

            return (new_annotations-self.annotations)*(1 if float(self.tracker_info['remind_diff'])>0 else -1) >= abs(float(self.tracker_info['remind_diff']))
        
        
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
                email_content='Website: {website_name}\n Link: {link}\n\n {message} \n\n====Original====\n {original}\n=====Update=====\n{update}'
                send_email(content_text = email_content.format(website_name=self.website_info["website_name"],
                                                                link=self.website_info["target_URL"],
                                                                message=self.website_info["email_messages"],
                                                                original=self.annotations,
                                                                update=new_annotations),
                            to_email =self.website_info["to_emails"])
                print('')

    return ListNewTracker
