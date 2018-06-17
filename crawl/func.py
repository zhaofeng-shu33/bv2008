#!usr/bin/python
# -*- coding: utf-8 -*-

# Apache License Version 2.0
# utility functions to extract data from bv2008.cn

from bs4 import BeautifulSoup

import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s - %(message)s')
logger = logging.getLogger('func.py')
from database import insert_project,insert_volunteer,insert_volunteer_project,update_volunteer,insert_organization
def get_project_joined_user(html_str,given_project_id):
    """Given html_str, extract the joined user id ,name,service_time
    Parameters
    ----------
    html_str : html marked text
    given_project_id : project id

    Returns
    ------- 
    None

    """
    # the top element is <html>
    soup_main = BeautifulSoup(html_str,'lxml')
    soup = soup_main.find(id='con2').table # table is contained within <div id="con2"/>
    # ignore the first row
    Ls=soup.find_all('tr')[1:]
    for row in Ls:
        td = row.find_all('td')
        given_service_time = None
        try:
            given_service_time = int(float(td[2].text.split(' ')[0].encode('ascii')))
        except IndexError as e:
            logging.error('len(td)<3,index error')
            continue
        except ValueError as e:
            logging.error('service time not a number')
            continue
        
        user_name = td[0].text
        user_url = None
        try:
            user_url = td[0].find(href=True)['href']
        except KeyError as e:
            logging.error('href not exit')
            continue
        user_id = None
        try:
            user_id = user_url.split('?id=')[1]
        except IndexError as e:
            logging.error('split failed')
            continue
        # when new entry is added to database
        if(insert_volunteer_project(volunteer_id=user_id,project_id=given_project_id)):
            logger.info(u'volunteer_id:{0}\tproject_id:{1}\n'.format(user_id,given_project_id))
        # resolve encoding
        if(type(user_name)==type(u'1')):
            user_name_utf_8 = user_name.encode('utf-8')
        if(insert_volunteer(volunteer_id=user_id,volunteer_name=user_name_utf_8,service_time=given_service_time)):
            logger.info(u'id: {0}\tname:{1}\ttime:{2}\n'.format(user_id,user_name,given_service_time))

def get_user_joined_project(html_str,given_organization_id):
    """Given html_str, extract the user joined project id ,name, time

    Parameters
    ----------
    html_str : html marked text
    given_organization_id : organization id

    Returns
    ------- 
    None

    """
    # the top element is <table>
    soup = BeautifulSoup(html_str,'lxml')
    # ignore the first row
    Ls=soup.find_all('tr')[1:]
    for row in Ls:
        td = row.find_all('td')
        project_time = None
        try:
            project_time = td[1].text
        except IndexError as e:
            logging.error('len(td)<1,index error')
            continue
        project_name = td[0].text
        project_url = None
        try:
            project_url = td[0].find(href=True)['href']
        except KeyError as e:
            logging.error('href not exit')
            continue
        given_project_id = None
        try:
            given_project_id = project_url.split('?id=')[1]
        except IndexError as e:
            logging.error('split failed')
            continue
        # when new entry is added to database
        # resolve encoding
        if(type(project_name)==type(u'1')):
            project_name_utf_8 = project_name.encode('utf-8')
        if(insert_project(project_id=given_project_id,project_name=project_name_utf_8,organization_id=given_organization_id,project_release_time=project_time)):
            logger.info(u'id: {0}\tname:{1}\ttime:{2}\n'.format(given_project_id,project_name,project_time))

def get_organization_detailed_info(html_str,given_organization_id):
    """Given html_str, extract the organization name and startup_time and insert into organization table

    Parameters
    ----------
    html_str : html marked text
    given_organization_id : organization id

    Returns
    ------- 
    None

    """
    # the top element is <html>
    soup = BeautifulSoup(html_str,'lxml')
    given_organization_name = None
    try:
        given_organization_name = soup.title.text.split('-')[0]
    except IndexError as e:
            logging.error('split failed')
            return
    desc_table = soup.find(class_ = 'l desc_txt').table
    try:
        tr7=desc_table.find_all('tr')[6] # try to locate the seventh row in the table
    except IndexError as e:
        logging.error('len(td)<7,index error')
        raise IndexError
    upper_organization_url = None
    try:
        upper_organization_url = tr7.find(href=True)['href']
    except KeyError as e:
        logging.error('href not exit')
        return
    upper_organization_id = None
    try:
        upper_organization_id = upper_organization_url.split('?id=')[1]
    except IndexError as e:
        logging.error('split failed')
        return
    upper_organization_id = int(upper_organization_id)
    tr6=desc_table.find_all('tr')[5]
    given_startup_time = tr6.td.text
    if(type(given_organization_name)==type(u'1')):
        given_organization_name_utf_8 = given_organization_name.encode('utf-8')

    if(insert_organization(given_organization_id, given_organization_name_utf_8, given_startup_time,upper_organization_id)):
        logger.info(u'id: {0}\tname:{1}\ttime:{2}\tupper_id:{3}\n'.format(given_organization_id,given_organization_name,given_startup_time,upper_organization_id))
    
    
def get_user_detailed_info(html_str,given_user_id):
    """Given html_str, extract the user gender and registration time and update volunteer table

    Parameters
    ----------
    html_str : html marked text
    given_user_id : user id

    Returns
    ------- 
    None

    """
    gender_info = None
    # the top element is <html>
    soup = BeautifulSoup(html_str,'lxml')
    gender_div = soup.find(class_='l desc_img gender0')    
    if(gender_div):
        gender_info = 'F'
    else:
        gender_div = soup.find(class_='l desc_img gender1')    
        if(gender_div):
            gender_info = 'M'
        else:
            logger.error('gender info missing for user %d' % given_user_id)
            raise KeyError('l_desc_img_gender0 or l_desc_img_gender1 not found')
    desc_table = soup.find(class_ = 'l desc_txt').table
    try:
        tr3=desc_table.find_all('tr')[2] # try to locate the third row in the table
    except IndexError as e:
        logging.error('len(td)<1,index error')
        raise IndexError
    registration_time = tr3.td.text
    if(update_volunteer(given_user_id, gender_info, registration_time)):
        logger.info(u'id: {0}\tgender:{1}\ttime:{2}\n'.format(given_user_id,gender_info,registration_time))

if __name__ == '__main__':
    # for testing purpose only
    test_html_str_project = '<table><tr/><tr><td><a href="/app/opp/view.php?id=1262105" target="_blank">清华大学艺术博物馆参观志愿活动</a></td><td>2017-12-18</td><td><font color="blue">自动结项</font></td></tr></table>'
    get_user_joined_project(test_html_str_project,given_organization_id=3474134)
    test_html_str_user = open('test_html_str_user.txt','rb').read()
    get_project_joined_user(test_html_str_user, given_project_id = 1262105)
    test_html_update_user = open('test_html_update_user.txt','rb').read()
    get_user_detailed_info(test_html_update_user,909860)
    test_html_organization_insert = open('test_html_organization_insert.txt','rb').read()
    get_organization_detailed_info(test_html_organization_insert,16287786)


