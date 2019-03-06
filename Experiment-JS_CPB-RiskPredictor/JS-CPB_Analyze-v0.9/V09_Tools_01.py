# coding:utf-8
#
# 本模块为需要处理的零散工具集合（1-5）
#
# 基本模块
import os,sys
import numpy as np
import sklearn.decomposition as skd
import sklearn.preprocessing as skp
import copy
import math
#
# 通用函数模块
def Extract_Date(date):
    # 01/02/2010 06:49:00
    year = date[6:10]
    month = date[:2]
    day = date[3:5]
    return year, month, day
#
# 实验一
# CERT4.2的Logon数据按月份分别存入对应目录下的文件，顺便创建月份目录
# 该程序运行时必须确保目标月份目录为空
# 使用了Label_1st用来标记第一次月份，以区分是否需要先关闭一个文件
Flag_0 = False
if Flag_0:
    print '..<<CERT4.2 Logon数据按月归类到月份目录>>..\n\n'
    # 定义一个已分析的月份列表
    Months_lst = []
    f_logon_path = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2-logon.csv'
    f_logon = open(f_logon_path, 'r')
    Logon_Src_lst = f_logon.readlines()
    f_logon.close()
    Label_1st = True
    for line_log in Logon_Src_lst[:]:
        line_lst = line_log.strip('\n').strip(',').split(',')
        # cert4.2 logon
        # id,date,user,pc,activity
        # {X1D9-S0ES98JV-5357PWMI},01/02/2010 06:49:00,NGF0157,PC-6056,Logon
        if line_lst[2] == 'user':
            continue
        year, month, day = Extract_Date(line_lst[1])
        cur_month = year + '-' + month
        if cur_month not in Months_lst:
            Months_lst.append(cur_month)
            # 如果不是第一个月，则需要先关闭文件标识
            if Label_1st == False:
                print Months_lst[-2], 'Logon数据分析完毕..\n'
                f_cur.close()
            # 创建月份
            if os.path.exists(sys.path[0] + '\\' + cur_month) == False:
                os.mkdir(sys.path[0] + '\\' + cur_month)
                # 创建文件
                f_cur = open(sys.path[0] + '\\' + cur_month + '\\' + cur_month + '_CERT4.2_Logon.csv', 'w')
                Label_1st == False
                for ele in line_lst[1:]:
                    f_cur.write(ele + ',')
                f_cur.write('\n')
                continue
        else:
            for ele in line_lst[1:]:
                f_cur.write(ele + ',')
            f_cur.write('\n')
            continue
#
#
# 提取CERT4.2用户的邮件数据，按照用户归类
Flag_1 = False
if Flag_1:
    Email_Path = r'G:\r4.2\email.csv'
    ldap_path = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2-2009-12.csv'
    f_ldap = open(ldap_path, 'r')
    CERT42_Users = []
    for line_ldap in f_ldap.readlines():
        line_lst = line_ldap.strip('\n').strip(',').split(',')
        # employee_name,user_id,email,role,business_unit,functional_unit,department,team,supervisor
        if line_lst[1] == 'user_id':
            continue
        CERT42_Users.append(line_lst[1])
    print 'CERT4.2用户统计完毕..\n', len(CERT42_Users), '\n'
    # 指定用户邮件内容保存目录
    Email_Dir = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2_Users_EmailRecord'
    for user in CERT42_Users:
        if os.path.exists(Email_Dir) == False:
            os.mkdir(Email_Dir)
        user_email_path = Email_Dir + '\\' + user + '_EmailRecord.csv'
        f_user_email = open(user_email_path, 'w')
        # CERT4.2 邮件格式
        # Fields: id, date, user, pc, to, cc, bcc, from, size, attachment_count, content
        # {R3I7-S4TX96FG-8219JWFF},01/02/2010 07:11:45,LAP0338,PC-5758,Dean.Flynn.Hines@dtaa.com;Wade_Harrison@lockheedmartin.com,Nathaniel.Hunter.Heath@dtaa.com,,Lynn.Adena.Pratt@dtaa.com,25830,0,middle f2 systems 4 july techniques powerful destroyed who larger speeds plains part paul hold like followed over decrease actual training international addition geographically side able 34 29 such some appear prairies still 2009 succession yet 23 months mid america could most especially 34 off descend 2010 thus officially southward slope pass finland needed 2009 gulf stick possibility hall 49 montreal kick gulf
        with open(Email_Path, 'r') as EmailRecords_lst:
            for line in EmailRecords_lst:
                line_lst = line.strip('\n').strip(',').split(',')
                if line_lst[0] == 'id':
                    continue
                if line_lst[2] != user:
                    continue
                else:
                    for ele in line_lst[1:-1]:
                        f_user_email.write(ele + ',')
                    f_user_email.write('\n')
                    continue
        f_user_email.close()
        print user, '邮件记录写入完毕..\n'

#
#
# 判断CERT4.2中三类Insiders的离职时间，以判断是否需要考虑2011-05的离职用户
# r4.2-1
# 顺便生成三类Insiders的用户列表代码，以及各自离职时间


#
#
# 从CERT4.2中的Insiders列表与Leave_Users列表中获取输入三个Insiders的离职日期
# 格式为
# KEW0198,2010-07-29,
# DAS1320,2010-07-30,
def Extract_Insiders(insiders_dir):
    insiders= []
    for file in os.listdir(insiders_dir):
        # r4.2-1-AAM0658.csv
        # print file, '\n'
        insiders.append(file[7:14])
    return insiders
Flag_2 = True
if Flag_2:
    # 首先获取CERT4.2中的Insiders列表
    Insiders_1 = Extract_Insiders(r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808' + '\\' + 'r5.2-1')
    Insiders_2 = Extract_Insiders(r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808' + '\\' + 'r5.2-2')
    Insiders_3 = Extract_Insiders(r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808' + '\\' + 'r5.2-3')
    print 'Insiders 1 like: ', Insiders_1[:3], '\n'
    print 'Insiders 2 like: ', Insiders_2[:3], '\n'
    print 'Insiders 3 like: ', Insiders_3[:3], '\n'
    #
    # 获取离职用户列表
    dst_52_dir = r'G:\GitHub\Essay-Experiments\Experiment-JobSatisfactory-201808\PythonCode0\JS-Risks_Analyze-0.9'
    f_leave = open(dst_52_dir + '\\' + 'CERT5.2-Leave-Users_OnDays_0.6.csv', 'r')
    Leave_Users = []
    for line_le in f_leave.readlines():
        line_lst = line_le.strip('\n').strip(',').split(',')
        if len(line_lst) < 2:
            continue
        leave_tmp = []
        leave_tmp.append(line_lst[0])
        leave_tmp.append(line_lst[1])
        Leave_Users.append(leave_tmp)
    print 'Leave_Users is like', Leave_Users[:3], '\n'
    #
    # 开始生成三个Insiders的列表
    # Insiders-1_Leave.csv
    f_2 = open(dst_52_dir + '\\' + 'Insiders-2_Leave.csv', 'w')
    for insider in Insiders_2:
        for leaver in Leave_Users:
            if insider != leaver[0]:
                continue
            else:
                f_2.write(leaver[0] + ',')
                f_2.write(leaver[1] + '\n')
    f_2.close()
    print 'Insiers_2 写入完毕..\n'

    f_1 = open(dst_52_dir + '\\' + 'Insiders-1_Leave.csv', 'w')
    for insider in Insiders_1:
        for leaver in Leave_Users:
            if insider != leaver[0]:
                continue
            else:
                f_1.write(leaver[0] + ',')
                f_1.write(leaver[1] + '\n')
    f_1.close()
    print 'Insiers_1 写入完毕..\n'

    f_3 = open(dst_52_dir + '\\' + 'Insiders-3_Leave.csv', 'w')
    for insider in Insiders_3:
        for leaver in Leave_Users:
            if insider != leaver[0]:
                continue
            else:
                f_3.write(leaver[0] + ',')
                f_3.write(leaver[1] + '\n')
    f_3.close()
    print 'Insiers_3 写入完毕..\n'

    print '生成Static模式下CERT4.2的GroundTruth标签..\n'
    Dst_Dir = sys.path[0] + '\\' + 'KMeans_OCSVM_Insiders_Predictor'
    # CERT4.2_Leave_Static_CPB_ATF-0.1.csv
    f_S_ATF = open(Dst_Dir + '\\' + 'CERT5.2_Static_CPB_ATF-0.1.csv', 'r')
    CERT42_Users = []
    for line in f_S_ATF.readlines():
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[0] == 'user_id':
            continue
        CERT42_Users.append(line_lst[0])
    CERT42_Labels = []
    for user in CERT42_Users:
        if user in Insiders_1 or user in Insiders_2 or user in Insiders_3:
            label = []
            label.append(user)
            label.append(1)
            CERT42_Labels.append(label)
        else:
            label = []
            label.append(user)
            label.append(-1)
            CERT42_Labels.append(label)
    f_GT = open(Dst_Dir + '\\' + 'CERT52_GroundTruth.csv', 'w')
    for line in CERT42_Labels:
        for ele in line:
            f_GT.write(str(ele) + ',')
        f_GT.write('\n')
    f_GT.close()
