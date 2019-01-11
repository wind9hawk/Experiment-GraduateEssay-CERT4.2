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
Flag_0 = True
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



