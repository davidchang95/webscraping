#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 23:29:59 2020

@author: davidchang
"""

from selenium import webdriver
import pandas as pd
import time
import re

url = 'https://www.facebook.com/careers/jobs/?page=1&results_per_page=100#search_result'

#filter to only United States
url = 'https://tinyurl.com/yb7g5wcd'
driver = webdriver.Chrome('/Users/davidchang/Desktop/chromedriver')
driver.get(url)

job_info = []

while(True):
    
    jobs = driver.find_elements_by_class_name('_8sef')
    for job in jobs:
        title = job.find_element_by_class_name('_8sel').text
        job_url = job.get_attribute('href')
        
        loc = job.find_element_by_class_name('_8sen')
        loc1 = loc.text.split('+')[0]
        if(len(loc1)) == 0:
            loc_list = []
        else:
            loc_list = loc1.splitlines()[0].split('|')
        if len(loc.text.split('+')) > 1:
            loc2 = loc.find_element_by_class_name('_8see')
            loc2 = loc2.get_attribute('data-tooltip-content').splitlines()
            loc_list.extend(loc2)
        loc_list = [i.lstrip(' ') for i in loc_list]
        loc_list = [i.rstrip(' ') for i in loc_list]
        
        areaofwork = job.find_element_by_class_name('_8sed')
        depts = areaofwork.find_elements_by_class_name('_8see')
        dept1 = areaofwork.find_element_by_class_name('_8see').text
        dept_list = [dept1]
        if len(depts) > 1:
            dept2 = depts[1].get_attribute('data-tooltip-content')
            dept2 = dept2.splitlines()
            dept_list.extend(dept2)
        
        job_info.append([title,loc_list,dept_list,job_url])

    if(len(driver.find_elements_by_xpath("//a[@class='_42ft _3nu9 _3nua _2xl7 _8q0b _8se6 _8ww0']"))==0):
        break
    
    next_page_url = driver.find_element_by_xpath("//a[@class='_42ft _3nu9 _3nua _2xl7 _8q0b _8se6 _8ww0']")
    driver.execute_script("arguments[0].scrollIntoView();", jobs[len(jobs)-1])    
    next_page_url.click()
    time.sleep(3)

jobs_df = pd.DataFrame(job_info, columns=['title','location','team','url'])

#%%

#drop duplicates doesnt work on lists like location and team, so do title/url
jobs_df = jobs_df.drop_duplicates(subset=['title','url'],keep='first') 
jobs_df.to_csv('fb_jobs.csv')

#clean up
del dept1, dept2, dept_list, depts, job_url, job, jobs, loc, loc1, loc2, loc_list, title
driver.quit()



#%%

data = pd.read_csv('/Users/davidchang/Desktop/fb_jobs.csv')
driver = webdriver.Chrome('/Users/davidchang/Desktop/chromedriver')

def add_experience(url):
    driver.get(url)
    if(driver.find_elements_by_xpath("//div[@class='_h46 _8lfy _8lfy']")):
        qualifications = driver.find_elements_by_xpath("//div[@class='_h46 _8lfy _8lfy']")[1].text
        years_exp = re.search('[0-9][0-9]*[+] years',qualifications)
        if(years_exp):
            years = re.search('[0-9][0-9]*', years_exp.group(0))
            return years.group(0)
    return 0 #if doesn't explicitly say then return 0

data['years_exp'] = data['url'].apply(add_experience)

data.to_csv('fb_jobs_with_years.csv')


