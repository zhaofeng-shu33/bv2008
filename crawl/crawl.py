#!usr/bin/python
# -*- coding: utf-8 -*-

# Apache License Version 2.0
# utility functions to crawl html pages from bv2008.cn

import requests
main_url = 'http://www.bv2008.cn/app/'

import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s - %(message)s')
logger = logging.getLogger('crawl.py')


from func import get_user_joined_project,get_project_joined_user,get_user_detailed_info,get_organization_detailed_info
from database import get_project_id,get_update_volunteer_list

def get_organization_initiate_project(organization_id):
    """
    given organization_id, get all the project the organization initiates
    Parameters
    ----------
    organization_id : int or list, if list, the first element of list is counted as main registration id

    Returns
    ------- 
    None
    """
    max_page_num = 10
    main_organization_id = None
    if(type(organization_id) == type([])):
        main_organization_id = organization_id[0]
    else:
        main_organization_id = organization_id
        organization_id = [organization_id]  # make a list
    # extract organization info
    request_url = main_url + 'org/view.php?id=%d'%main_organization_id
    response=requests.get(request_url)
    if not(response.status_code == 200):
        raise ValueError("status code not equal 200")
    get_organization_detailed_info(response.text,main_organization_id)
    for o_id in organization_id:     
        for i in range(1,max_page_num):
            request_url = main_url + 'api/view.php?m=get_opps&type=2&id=%d&p=%d'%(o_id,i)
            response=requests.get(request_url)
            if not(response.status_code == 200):
                raise ValueError("status code not equal 200")
            # the top element is <html> for the first page
            if(response.text.count('tr')<3):# empty table
                break
            get_user_joined_project(response.text,main_organization_id)

def update_project_joined_user(organization_id = None):
    """
    select project ids from table 'project' and get the joined user html table from bv2008.cn,
    then call the function 'get_project_joined_user'
    Parameters
    ----------
    organization_id : int

    """
    for i in get_project_id(organization_id):
        request_url = main_url + 'opp/view.php?id=%d'%(int(i[0]))
        response=requests.get(request_url)
        if not(response.status_code == 200):
            logging.error('request url %s failed' % request_url)
            raise ValueError("status code not equal 200")
        if(response.text.find('error_icon errno')>0): #项目不存在或不公开招募
            continue
        get_project_joined_user(response.text,given_project_id = int(i[0]))

def update_volunteer_info():
    """
    select volunteer ids from table 'volunteer' and get user html table from bv2008.cn,
    then call the function 'get_user_detailed_info'
    """
    for i in get_update_volunteer_list():
        request_url = main_url + 'user/view.php?id=%d'%(int(i[0]))
        response=requests.get(request_url)
        if not(response.status_code == 200):
            raise ValueError("status code not equal 200")
        # handle js url redirection
        if(response.text[-9:] == '</script>'):
            new_user_url_start = response.text.find('http')
            new_user_url_end = response.text.find('";</script>')
            if not(new_user_url_end>0):
                raise ValueError(response.text)
            new_user_url = response.text[new_user_url_start:new_user_url_end]
            logging.info('request redirected url: %s' % new_user_url)
            response = requests.get(new_user_url)
            if not(response.status_code == 200):
                raise ValueError("status code not equal 200")
        get_user_detailed_info(response.text,given_user_id = int(i[0]))
           
if __name__ == '__main__':
    # for testing purpose only
    organization_list = [3474414,3474395] #,3474384,3474378,3474376,3474316,3471958,3470375]
    for i in organization_list:
        get_organization_initiate_project(organization_id = i)
        update_project_joined_user(organization_id = i)
    update_volunteer_info()

