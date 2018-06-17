#!usr/bin/python
# -*- coding: utf-8 -*-

# Apache License Version 2.0
# rountine to generate html table for Task 清华本科不同院系比较

import MySQLdb

db = MySQLdb.connect('localhost','root','zf545598','bv2008',init_command='set names utf8')

cursor = db.cursor()

# first, get all department
cursor.execute('select organization_id,organization_name from organization where upper_organization_id = 3471958 or upper_organization_id = 1')

Ls = []
for org in cursor.fetchall():
    # total project
    cursor.execute('select count(*) from project where organization_id = %d'%org[0])
    project_cnt = cursor.fetchone()[0]
    cursor.execute('select volunteer.volunteer_id from volunteer,volunteer_project,project where volunteer.volunteer_id = volunteer_project.volunteer_id and volunteer_project.project_id = project.project_id and project.organization_id = %d group by volunteer.volunteer_id;'%org[0])
    person_cnt = len(cursor.fetchall())    
    cursor.execute('select volunteer.volunteer_id from volunteer,volunteer_project,project where volunteer.volunteer_id = volunteer_project.volunteer_id and volunteer_project.project_id = project.project_id and volunteer.gender = \'F\' and project.organization_id = %d group by volunteer.volunteer_id;'%org[0])
    female_person_cnt = len(cursor.fetchall())
    female_persent = None
    try:
        female_persent = female_person_cnt*100/person_cnt
    except ZeroDivisionError as e:
        raise Exception('person_cnt = zero for org id = %d' % org[0])
    Ls.append([org[1],project_cnt,person_cnt,female_persent])
    for j in range(2012,2018):
        cursor.execute("select count(*) from volunteer_project,project where project.organization_id = {0} and volunteer_project.project_id = project.project_id and year(project.release_time) = {1};".format(org[0],j))
        Ls[-1].append(cursor.fetchone()[0])


st = ''
Ls.sort(reverse=True, key = lambda x:x[2]) # sort by person_cnt
for i in Ls:
    st += '\t\t\t<tr>'
    st += '<td>' + i[0] + '</td>' # org name
    st += '<td>' + str(i[1]) + '</td>'
    st += '<td>' + str(i[2]) + '</td>'
    if(i[3]>65):
        st += '<td class="female_large">' + str(i[3]) + '%</td>'
    else:
        st += '<td>' + str(i[3]) + '%</td>'
    for j in range(6):
        st += '<td>' + str(i[4+j])+ '</td>'
    st += '</tr>\n'

f = open('thu_department_compare.txt','wb')
f.write(st)
f.close()
#sogou qimpanel watchdog 
