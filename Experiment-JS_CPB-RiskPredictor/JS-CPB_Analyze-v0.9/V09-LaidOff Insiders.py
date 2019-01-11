# coding:utf-8
# 本程序主要用于分析CERT4.2中LDAP文件集合中体现的用户中途离职的情况
# 初步结果应包括：
# 1. 2009-12至2011-05期间所有离开单位的员工
# 2. 2009-12至2011-05期间所有加入单位的员工
# 3. 所有离职与入职员工的LDAP信息
# 4. 跳槽场景中30个用户的LDAP信息
# 5. 30个跳槽用户所属组织团队、部门、职能部门以及事业部门中的离职、入职人员情况统计

import os
import sys
#
# 定义一个提取时间的函数，具体到日子
def GetDate(date):
    # like: 01/02/2010 09:03:11
    year = date[6:10]
    month = date[:2]
    day = date[3:5]
    return year + '-' + month + '-' + day
# 定义一个读取Logon数据以确定用户最后一天上班的日期==最后一次发邮件的日期，以此作为用户的离职日期
def Extract_LastLogonDay(user, logon_lst):
    # CERT4.2 Logon数据格式
    # id,date,user,pc,activity
    # {X1D9-S0ES98JV-5357PWMI},01/02/2010 06:49:00,NGF0157,PC-6056,Logon
    # 提取每个用户的所有登录记录，保存在Logon数据的目录下
    # 提取最后一次Logon登录的日期作为其离职日期返回
    logon_dir = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2_Logon_ByUsers_0.6' + '\\' + user
    f_user_logon = open(logon_dir + '\\' + 'V09_Logon_Data.csv', 'w')
    last_logon_date = '2010-01-01'
    for line_log in logon_lst:
        line_lst = line_log.strip('\n').strip(',').split(',')
        if line_lst[1] == 'date':
            continue
        if line_lst[2] != user:
            continue
        else:
            date = GetDate(line_lst[1])
            if line_lst[-1] == 'Logon':
                last_logon_date = date
            f_user_logon.write(date + ',')
            for ele in line_lst[2:]:
                f_user_logon.write(ele + ',')
            f_user_logon.write('\n')
            continue
    f_user_logon.close()
    return last_logon_date

#
#
print '首先分析CERT4.2数据中所有离职与入职的员工信息...\t...[laid off/in month, user ldap]...\n'
# 首先比较发现变化的用户user_id
# 然后记录该用户信息到Users_Laid/In中
# 采用一个时间计数器来定位用户变化的月份
Users_CERT = [] # 原始用户列表，以user_id形式存储
Users_LDAP = [] # 原始用户的ldap信息
Users_LaidOff = []
Users_EngageIn = []
MonthCnt = 1 #从2010-01开始
MonthList = []
fileMonth = []
# 目标目录G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\LDAP
dirPath = os.path.dirname(sys.path[0]) + '\\' + 'LDAP'
for file in os.listdir(dirPath):
    # 2009-12.csv
    MonthList.append(file[:7])
    file = dirPath + '\\' + file
    fileMonth.append(file)
print '所有需要分析的月份有： ', MonthList, '\n'
print '所有需要分析的LDAP文件有： ', fileMonth, '\n'
##
##
##程序块之间间断3行
# 以第一个月份的用户作为初始用户列表，从中提取全部用户user_id，然后开始比较之后每个用户的加入与离开
f = open(fileMonth[0], 'r')
f_lst = f.readlines()
f.close()
# 指定CERT4.2的用户登录数据
Logon_Path = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2-logon.csv'
f_logon = open(Logon_Path, 'r')
Logon_lst = f_logon.readlines()
f_logon.close()
f_w = open('CERT4.2-Leave-Users_OnDay_0.9.csv', 'w') # 定义一个记录离职员工的文件，注意离职leave与解雇laid off不同
f_w.write('Leave  Users in CERT4.2 from 2009-12 to 2011-05\n')
for usr in f_lst:
    line = usr.strip('\n').strip(',').split(',')
    # CERT4.2 LDAP数据字段格式
    # employee_name,user_id,email,role,business_unit,functional_unit,department,team,supervisor
    if line[1] == 'user_id':
        continue
    Users_CERT.append(line[1])
    Users_LDAP.append(usr)
print 'CERT users初始化完毕...\t', Users_CERT[:10], '\n'

# 为所有用户生成独立的Logon数据
CERT42_Users_LastDay = []
for user in Users_CERT:
    last_day = Extract_LastLogonDay(user, Logon_lst)
    print user, 'Logon数据提取完毕..\n'
    lastday = []
    lastday.append(user)
    lastday.append(last_day)
    CERT42_Users_LastDay.append(lastday)

#
# 开始循环比较后续的LDAP文件，筛选出其中的变化用户
j = 0
while j < len(Users_CERT):
    # 开始判断离职的用户
    if CERT42_Users_LastDay[j][1] < '2011-05-01':
        # 说明该用户未一直工作
        # 该用户离职
        laid_ldap = []
        laid_ldap.append(CERT42_Users_LastDay[j][0])
        laid_ldap.append(CERT42_Users_LastDay[j][1])
        laid_ldap.append(Users_LDAP[j].strip('\n'))
        Users_LaidOff.append(laid_ldap)
        #Users_LDAP.remove(Users_LDAP[j])
        #Users_CERT.remove(user) # 从当前用户集合中删除该用户
        print Users_CERT[j], CERT42_Users_LastDay[j], ' 离职 ', '月份 ', CERT42_Users_LastDay[j][1], ':', laid_ldap, '\n'
        j += 1
    else:
        j += 1

Users_LaidOff_sort = sorted(Users_LaidOff, key=lambda t: t[1])
for usr in Users_LaidOff_sort:
    print usr[0], '离职月份： ', usr[1], 'LDAP信息： ', usr[2], '\n'
    f_w.write(usr[0])
    f_w.write(',')
    f_w.write(usr[1])
    f_w.write(',')
    f_w.write(usr[2])
    f_w.write('\n')
print '总共离职用户为： ', len(Users_LaidOff), '\n'
# print '入职用户为： ', Users_EngageIn, '\n'
sys.exit()

