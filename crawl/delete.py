#!usr/bin/python
# -*- coding: utf-8 -*-

# Apache License Version 2.0
# this script file is only used in special cases when an organization need to be cleaned out
import MySQLdb

db = MySQLdb.connect('localhost','root','zf545598','bv2008',init_command='set names utf8')

cursor = db.cursor()

# to be cleaned out
organization_id = 3474376

def clean_volunteer_table(volunteer_id):
    cursor.execute('delete from volunteer where volunteer_id = %d'% volunteer_id)
    db.commit()
def no_other_project_joined(volunteer_id):
    cursor.execute('select volunteer_project.project_id from volunteer_project, project where volunteer_project.volunteer_id = {0} and volunteer_project.project_id = project.project_id and project.organization_id <> {1}'.format(volunteer_id,organization_id))
    if(cursor.fetchone()):
        return True
    return False
   
def clean_volunteer_project_table(project_id):
    cursor.execute('select volunteer_id from volunteer_project where project_id = %d' % project_id)
    for j in cursor.fetchall():
        if(no_other_project_joined(j[0])):
            clean_volunteer_table(j[0])
        cursor.execute('delete from volunteer_project where volunteer_id = {0} and project_id = {1}'.format(j[0],project_id))
        db.commit()

cursor.execute('select project_id from project where organization_id = %d' % organization_id)

for i in cursor.fetchall():
    clean_volunteer_project_table(i[0])
    cursor.execute('delete from project where project_id = %d'% i[0])
    db.commit()

cursor.execute('delete from organization where organization_id = %d' % organization_id)
db.commit()

