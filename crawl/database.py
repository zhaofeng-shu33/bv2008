#!usr/bin/python
# -*- coding: utf-8 -*-

# Apache License Version 2.0
# utility functions to insert data into mysql bv2008

import MySQLdb

db = MySQLdb.connect('localhost','root','zf545598','bv2008',init_command='set names utf8')

cursor = db.cursor()

import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s[line:%(lineno)d] - %(levelname)s - %(message)s')
logger = logging.getLogger('database.py')
def insert_organization(organization_id,organization_name, startup_time,upper_organization_id):
    """
    insert one record into table 'organization'
    Parameters
    ----------
    organization_id : int
    organization_name : str
    startup_time: str
    upper_organization_id: int    
        
    Returns
    ------- 
    is_database_updated: boolean
    """
    try:
        cursor.execute("insert into organization (organization_id,organization_name,startup_time,upper_organization_id) values ({0},'{1}','{2}',{3})".format(organization_id,organization_name,startup_time,upper_organization_id))
    except MySQLdb.IntegrityError as e:
        # ignore duplicate entry here
        if(e[0]==1062):  
            return False                      
        logging.error(e)
        db.rollback()
    db.commit()
    return True

def insert_volunteer(volunteer_id,volunteer_name,service_time,registration_date='2000-1-1'):
    """
    insert one record into table 'volunteer'
    Parameters
    ----------
    volunteer_id : int
    volunteer_name : str
    registration_date: str
    service_time : int
        
    Returns
    ------- 
    is_database_updated: boolean
    """
    try:
        cursor.execute("insert into volunteer (volunteer_id,name,registration_date,service_time) values ({0},'{1}','{2}',{3})".format(volunteer_id,volunteer_name,registration_date,service_time))
    except MySQLdb.IntegrityError as e:
        # ignore duplicate entry here
        if(e[0]==1062):  
            return False                      
        logging.error(e)
        db.rollback()
    db.commit()
    return True

def insert_project(project_id,project_name,organization_id=123,project_release_time='2000-1-1'):
    """
    insert one record into table 'project'
    Parameters
    ----------
    project_id : int
    project_name : str
    project_release_time: str
    organization_id : int
    Returns
    ------- 
    is_database_updated: boolean
    """
    try: # 单引号转义
        cursor.execute("insert into project (project_id,name,release_time,organization_id) values ({0},'{1}','{2}',{3})".format(project_id,MySQLdb.escape_string(project_name),project_release_time,organization_id))
    except MySQLdb.IntegrityError as e:
        # ignore duplicate entry here
        if(e[0]==1062):      
            return False                  
        logging.error(e)
        db.rollback()
    db.commit()
    return True

def insert_volunteer_project(volunteer_id,project_id):
    """
    insert one record into table 'volunteer_project'

    Parameters
    ----------
    volunteer_id : int
    project_id : int

    Returns
    ------- 
    is_database_updated: boolean
    """
    # first test whether the database has the entry
    cursor.execute("select vp_id from volunteer_project where project_id = {0} and volunteer_id = {1};".format(project_id,volunteer_id))
    if not(cursor.fetchone()):
        try:
            cursor.execute("insert into volunteer_project (volunteer_id,project_id) values ({0},{1});".format(volunteer_id,project_id))
        except MySQLdb.IntegrityError as e:
            # ignore duplicate entry here
            logger.error(e)
            db.rollback()
        db.commit()
        return True
    else:
        return False

def get_project_id(organization_id = None):
    """
    get project id from table 'project'
    Parameters
    ----------
    None

    Returns
    ------- 
    project id list
    """
    if(organization_id):
        cursor.execute("select project_id from project where organization_id = %d" % organization_id )
    else:
        cursor.execute("select project_id from project;")
    return cursor.fetchall()

def get_update_volunteer_list():
    """
    Test whether volunteer table needs update for the given volunteer_id

    Parameters
    ----------
    None

    Returns
    ------- 
    volunteer_id list

    """
    cursor.execute('select volunteer_id from volunteer where gender is null')
    return cursor.fetchall()

def update_volunteer(volunteer_id,volunteer_gender, registration_date = '2000-1-1'):
    """
    update volunteer table
    this function returns true if 
    volunteer_gender and registration_date are added to database

    Parameters
    ----------
    volunteer_id : int
    volunteer_gender : str,'M' or 'F'
    registration_date : str

    Returns
    ------- 
    is_database_updated: boolean

    """
    try:
        cursor.execute("update volunteer set gender = '{0}', registration_date = '{1}' where volunteer_id = {2}".format(volunteer_gender,registration_date,volunteer_id))
    except Exception as e:
        return False                  
        logging.error(e)
        db.rollback()
    db.commit()
    return True
        
if __name__ == '__main__':
    # for testing purpose only
    print(insert_volunteer(volunteer_id=16563809,volunteer_name='冯琪凡',service_time=21,registration_date='2015-12-08'))
    print(insert_volunteer(volunteer_id=60853739,volunteer_name='张翼',service_time=4))
    print(insert_project(project_id=1262105,project_name='清华大学艺术博物馆参观志愿活动',organization_id=3474134,project_release_time='2017-12-11'))
    print(insert_volunteer_project(volunteer_id=16563809,project_id=1262105))
    print('update_volunteer',update_volunteer(volunteer_id = 282580, volunteer_gender = 'F', registration_date = '2012-05-19'))
    print('insert_organization',insert_organization(organization_id = '3474135',organization_name = '清华大学电子系紫荆志愿者支队', startup_time = '	2012-04-24', upper_organization_id = '3472185'))
