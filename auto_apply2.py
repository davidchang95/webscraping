#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 27 16:03:14 2020

@author: davidchang
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 00:21:29 2020

@author: davidchang
"""

from selenium import webdriver
import pandas as pd
import time
import os
import math
#%%

"""
instead of iterating through all the job description page and clicking on apply button and 
loading application page, just get the link for actual application page and save into dataframe,
then make script that iterates through those links  
"""

data = pd.read_csv('/Users/davidchang/Desktop/fb_jobs.csv')
driver = webdriver.Chrome('/Users/davidchang/Desktop/chromedriver')

def add_app_url(url):
    driver.get(url)
    if(driver.find_element_by_xpath("//a[@class='_42ft _8ww0 _3nu9 _3nua _8q0b _8lfr _8lfg']")):
        apply_button = driver.find_element_by_xpath("//a[@class='_42ft _8ww0 _3nu9 _3nua _8q0b _8lfr _8lfg']")
        app_url = apply_button.get_attribute('href')
        return app_url
    return 0


data['app_url'] = data['url'].apply(add_app_url)
app_url_list = data['app_url']
app_url_list.to_csv('app_urls.csv')
driver.quit()


#%%

"""
get all the variations of my email 
convert int to binary to figure out where to put period in address

decimal:           1            2                3              4 
binary:            1           10               11            100
reverse:           1           01               11            001
text:            d.avid      da.vid           d.a.vid        dav.id


in get_email, add periods into locations correlating to 1 in binary number. 
dot_count keeps track of periods which add to length, to accurately add periods later in string

"""

binary = []
#convert int to binary
for i in range(1, 2000):
   binary.append([i, bin(i).lstrip('0b'), bin(i).lstrip('0b')[::-1]])

bi_df = pd.DataFrame(binary, columns=['dec','bi', 'bi_reverse'])


def get_email(bi_reverse):
    email = 'fakeemail@gmail.com'
    dot_count = 0
    for i in range(0,len(bi_reverse)):
        if bi_reverse[i] == '1': 
            email = email[:i+dot_count+1] + '.' + email[i+dot_count+1:]
            dot_count = dot_count+1
    return email

bi_df['email'] = bi_df['bi_reverse'].apply(get_email)
bi_df.to_csv('email_addresses.csv')

emails = pd.read_csv('email_addresses.csv')
emails = emails['email']

#%%

"""
Navigating through actual application page: 
3 scenarios

THREE SCENARIOS (only going to apply to step 1)
1. job is in US (work elegibility)
2. Singapore(asks for citizenship)
3. anywhere else

"""

driver = webdriver.Chrome('/Users/davidchang/Desktop/chromedriver')

for i in range(1, len(app_url_list)-1): 
    print(i)
    driver.get(app_url_list[i])
    header = driver.find_element_by_xpath("//div[@class='_3m9 _1n-z _6hy- _7wij']")
    driver.execute_script("arguments[0].scrollIntoView();", header)  

    #close covid19 pop up at bottom
    if(len(driver.find_elements_by_xpath("//button[@class='_90e-']"))>0):
        covid19 = driver.find_element_by_xpath("//button[@class='_90e-']")
        covid19.click()

    """
    Step 1 resume
    uncheck automatic parse resume
    upload resume, make sure spyder is in correct current directory 
    when getting file (shows on upper right of screen)
    """
    dont_parse = driver.find_element_by_xpath("//label[@for='parseResume']")
    dont_parse.click()
    
    upload = driver.find_element_by_xpath("//input[@class='_n _5f0v']")
    upload.send_keys(os.getcwd()+"/resume.pdf")
    
    driver.execute_script("arguments[0].scrollIntoView();", dont_parse) 

    """
    Step 2 contact info 
    Site will throw an error if you just type in location and dont select from suggested drop down
    added time.sleep to wait for that to load
    """
    name = driver.find_element_by_xpath("//input[@name='candidateName']")
    name.send_keys('John Smith')

    email = driver.find_element_by_xpath("//input[@name='candidateEmail']")
    
    email_num = math.floor(i/3)
    
    
    #email_address = 'zuck@fb.com'
    email.send_keys(emails[email_num])

    phone = driver.find_element_by_xpath("//input[@name='candidatePhone']")
    phone.send_keys('4081231234')
    time.sleep(1)
    location = driver.find_element_by_xpath("//input[@name='candidateLocationName']")
    location.send_keys('Cupertino, CA')

    time.sleep(2)
    #location_select = driver.find_element_by_xpath("//div[@class='uiTypeaheadView uiContextualTypeaheadView']")
    location_select = driver.find_element_by_xpath("//div[@class='uiContextualLayer uiContextualLayerBelowLeft']")
    location_select.click()

    no_work_exp = driver.find_element_by_xpath("//label[@class='_kv1 _55sg uiInputLabelInput']")
    driver.execute_script("arguments[0].scrollIntoView();", no_work_exp)
    

    """
    Step 3 past experience
    for start/end month and year, could not find element of the drop down menu
    insteaduse execute_script with to set the actual value itself so actual text on webpage
    doesn't get updated
    """
    employer0 = driver.find_element_by_xpath("//input[@name='workEmployerNames[0]']")
    employer0.send_keys('Google')

    position0 = driver.find_element_by_xpath("//input[@name='workPositionNames[0]']")
    position0.send_keys('SWE')
    
    location0 = driver.find_element_by_xpath("//input[@name='workLocationNames[0]']")
    location0.send_keys('Mountain View, California')
    
    description0 = driver.find_element_by_xpath("//textarea[@name='workDescriptions[0]']")
    description0.send_keys('Machine Learning')

    startmm0 = driver.find_element_by_xpath("//input[@name='workStartMonths[0]']")
    driver.execute_script("arguments[0].value='4';", startmm0)
    startyy0 = driver.find_element_by_xpath("//input[@name='workStartYears[0]']")
    driver.execute_script("arguments[0].value='2015';", startyy0)

    currentwork = driver.find_element_by_xpath("//div[@class='_25jq']")
    currentwork.click()
    driver.execute_script("arguments[0].scrollIntoView();", currentwork)

    addmore = driver.find_element_by_xpath("//button[@class='_42ft _3ma _3nu9 _3nua _8q0b _56ta']")
    addmore.click()

    employer1 = driver.find_element_by_xpath("//input[@name='workEmployerNames[1]']")
    employer1.send_keys('Airbnb')

    position1 = driver.find_element_by_xpath("//input[@name='workPositionNames[1]']")
    position1.send_keys('SWE')

    location1 = driver.find_element_by_xpath("//input[@name='workLocationNames[1]']")
    location1.send_keys('San Francisco, California')

    description1 = driver.find_element_by_xpath("//textarea[@name='workDescriptions[1]']")
    description1.send_keys('Software engineering stuff')

    startmm1 = driver.find_element_by_xpath("//input[@name='workStartMonths[1]']")
    driver.execute_script("arguments[0].value='6';", startmm1)
    startyy1 = driver.find_element_by_xpath("//input[@name='workStartYears[1]']")
    driver.execute_script("arguments[0].value='2010';", startyy1)

    endmm1 = driver.find_element_by_xpath("//input[@name='workEndMonths[1]']")
    driver.execute_script("arguments[0].value='2';", endmm1)
    endyy1 = driver.find_element_by_xpath("//input[@name='workEndYears[1]']")
    driver.execute_script("arguments[0].value='2015';", endyy1)

    driver.execute_script("arguments[0].scrollIntoView();", addmore)

    """
    Step 4 skills
    
    """
    
    skills = driver.find_element_by_xpath("//textarea[@title='Areas of expertise...']")
    skills.send_keys('SQL, Python, R, Excel') 
    driver.execute_script("arguments[0].scrollIntoView();", addmore)
    
    driver.execute_script("arguments[0].scrollIntoView();", skills)

    """
    Step 5 education
    like year/month of experience, can't access web element for college degree
    so just directly set the value attribute, which won't update the text shown in webpage
    """
    college = driver.find_element_by_xpath("//input[@name='collegeSchoolNames[0]']")
    college.send_keys('University of California, Berkeley')

    degree = driver.find_element_by_xpath("//input[@name='collegeDegreeNames[0]']")
    driver.execute_script("arguments[0].value='Bachelors';", degree)
    
    concentration1 = driver.find_element_by_xpath("//input[@name='collegeConcentration1Names[0]']")
    concentration1.send_keys('Computer Science')
    
    concentration2 = driver.find_element_by_xpath("//input[@name='collegeConcentration2Names[0]']")
    concentration2.send_keys('Statistics')

    highschool = driver.find_element_by_xpath("//input[@name='highSchoolName']")
    highschool.send_keys('Stuyvesant High School')

    url_addmore = driver.find_element_by_xpath("//button[@class='_42ft _3ma _3nu9 _3nua _8q0b _4hkm _8l8j _4td4']")
    driver.execute_script("arguments[0].scrollIntoView();", url_addmore)

    
    """
    Step 7 location
    say yes for all locations
    pulling all the buttons yes/no for each location
    iterating through those buttons clicking yes, skipping no
    check for ok with remote work
    #find all checkboxes on page, remote is 5th checkbox
    """
    loc_number = len(driver.find_elements_by_class_name('_51mx'))
    locations = driver.find_elements_by_xpath("//label[@class='_1_wj uiInputLabelLabel']")

    for i in range(0,loc_number*2-1):
        if i%2 == 0:
            locations[i].click()

    """
    equal employment opportunity stuff
    for legally authroized to work, need visa, gender, disability
    
    THREE SCENARIOS
    1. job is in US (work elegibility)
    2. Singapore(asks for citizenship)
    3. anywhere else
    """

    yesbuttons = driver.find_elements_by_xpath("//label[@class='_1_wj uiInputLabelLabel']")

    #legally authorized to work
    yesbuttons[loc_number*2].click()
    #need visa
    yesbuttons[loc_number*2+3].click()
    #north korea citizen?
    yesbuttons[loc_number*2+5].click()


    note = driver.find_element_by_xpath("//div[@class='_1_wi _3-98']")
    
    driver.execute_script("arguments[0].scrollIntoView();", note)  

    
    #dont disclose gender
    yesbuttons[loc_number*2+8].click()

    yesbuttons = driver.find_elements_by_xpath("//label[@class='_1_wj _3-97 uiInputLabelLabel']")

    #dont disclose race
    yesbuttons[7].click()
    driver.execute_script("arguments[0].scrollIntoView();", yesbuttons[7]) 

    #veteran
    yesbuttons[11].click()
    driver.execute_script("arguments[0].scrollIntoView();", yesbuttons[11]) 

    #disability
    yesbuttons[14].click()
    footnotes = driver.find_elements_by_xpath("//div[@class='_qag']")
    driver.execute_script("arguments[0].scrollIntoView();", footnotes[len(footnotes)-1])  
    
    submit_app = driver.find_element_by_xpath("//button[@name='submit']")
    submit_app.click()
    
    








