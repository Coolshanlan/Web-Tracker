
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests
import logging
from .basic_tracker import DynamicTracker, BasicTracker


def get_NumberTracker(basic_tracker):
    class NumberTracker(basic_tracker):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.achieved =False
            self.last_annotation=None
            
        def post_process(self,annotations):
            if 'remove_word' in self.website_info.keys():
                if isinstance(self.website_info['remove_word'],list):
                    for word in self.website_info['remove_word']:
                        annotations = annotations.replace(word,'')
                else:
                    annotations = annotations.replace(word,'')
            return float(annotations)
            
        def checking(self,new_annotations):
            if self.last_annotation is None:
                self.last_annotation = new_annotations
            
            # record history
            if self.last_annotation != new_annotations:
                self.last_annotation = new_annotations
                self.logger.debug(f'Annotation different record:{new_annotations}')
            
            # check if number achieve the target number    
            if "target_number" in self.website_info.keys():
                target_info=self.website_info["target_number"]
                
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

            return (new_annotations-self.annotations)*(1 if float(self.website_info['remind_diff'])>0 else -1) >= abs(float(self.website_info['remind_diff']))
        
        
    return NumberTracker
