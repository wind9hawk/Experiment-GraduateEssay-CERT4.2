# coding:utf-8
# 这是一个面向对象的，借助SVM构建的用户JSR的预测器类
# 该类具有以下核心方法/属性：
# class_method_1: 构造初始化（数据复制准备）
# class_method_2: 析构函数
# class_method_3: JS特征提取函数
# class_method_4: train_predictor
# class_method_5: validate_predictor
# class_method_6: run_predicotr
# 下面，开始集中精力，完成该大类的编写实现，注意：
# 1. 阶段性验证，确保每一步完成后都是正确的；
# 2. 特殊事例验证；

import sys,os
import numpy as np
import sklearn.preprocessing as skp
import copy
import shutil
import math
from sklearn.svm import SVC
import pandas as pd
import sklearn.preprocessing as skp
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
import sklearn.decomposition as skd



def Get_User_OCEAN(user, f_ocean_lst):
    for line in f_ocean_lst:
        # data like:
        # employee_name,user_id,O,C,E,A,N
        # Maisie Maggy Kline,MMK1532,17,17,16,22,28
        line_lst = line.strip('\n').strip(',').split(',')
        if line_lst[1] == 'user_id':
            continue
        if line_lst[1] == user:
            tmp_ocean = []
            tmp_ocean.append(line_lst[1])
            for ele in line_lst[2:]:
                tmp_ocean.append(float(ele))
            return tmp_ocean  # 6-format: user_id, o, c, e, a, n
        else:
            continue

def CalCPBs(user_ocean):
    # user_ocean； user_id, o,c,e,a,n
    # O_Score, C_Score, E_Score, A_Score, N_Score
    O_Score = user_ocean[1]
    C_Score = user_ocean[2]
    E_Score = user_ocean[3]
    A_Score = user_ocean[4]
    N_Score = user_ocean[5]
    #CPB_1Score = A_Score * (-0.34) + A_Score * 0.36 * (-0.40)
    #CPB_2Score = C_Score * (-0.52) + A_Score * 0.36 * (-0.41)
    # CPB-I_Self = (-0.43) * A_Score + (-0.16) * C_Score + (-0.24) * -N_Score + 0.25 * E_Score + (-0.30) * O_Score
    # CPB-O_Self = (-0.41) * A_Score + (-0.44) * C_Score + (-0.47) * -N_Score + (-0.12) * E_Score + (-0.25) * O_Score
    CPB_1Score = (-0.43) * A_Score + (-0.16) * C_Score + (-0.24) * (-1 * N_Score) + 0.25 * E_Score + (-0.30) * O_Score
    CPB_2Score = (-0.41) * A_Score + (-0.44) * C_Score + (-0.47) * (-1 * N_Score) + (-0.12) * E_Score + (-0.25) * O_Score
    return CPB_1Score, CPB_2Score

# 定义一个给定user与ldap_src，自动返回其组织结构OS信息的函数
def Get_User_LDAP(user, f_ldap_lst):
    # 不考虑CEO的特征，因为CEO压根没有离职，也不是Insiders
    user_ldap = []
    Find_Label = False
    for line in f_ldap_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # LDAP文件内容格式
        # employee_name,user_id,email,role,projects,business_unit,functional_unit,department,team,supervisor
        # cert4.2 ldap格式
        # employee_name,user_id,email,role,business_unit,functional_unit,department,team,supervisor
        if line_lst[1] == 'user_id':
            continue
        if len(line_lst) < 9:
            # CEO
            continue
        if line_lst[1] == user:
            Find_Label = True
            # 补充上了项目+LDAP信息
            # 项目信息用于日后分析备用
            user_ldap.append(user)
            user_ldap.append(line_lst[4]) # BU
            user_ldap.append(line_lst[5])
            user_ldap.append(line_lst[6])
            user_ldap.append(line_lst[7])
            # user_ldap.append(line_lst[8]) # team
            break
    # print user, 'Project + LDAP提取完毕..\n', user_ldap, '\n'
    if Find_Label == True:
        return user_ldap  # 6-format: user_id, bu, fu, dpt, team
    else:
        return 'Not Found'

def Get_User_LC_Feat(user_id, lc_lst, month):
    # 通过该函数，可以得到与user_id在划定时间周期内通讯的离职员工邮件特征
    # 把该时间段内所有与离职员工通讯看作和一个虚拟的离职用户通讯
    print '开始计算', user_id, '的leave_contacts邮件特征..\n'
    user_lc_feat = []

    user_lcontacts = [] # 时间段内与目标用户关联的离职用户列表，用于后续计算dis_OCEAN/dis_OS
    #user_email_ratio = 0.0
    user_cnt_send = 0.0
    #user_cnt_recv = 0.0
    user_send_size = 0.0
    #user_recv_size = 0.0
    user_send_attach = 0.0
    #user_recv_attach = 0.0
    user_send_days = []
    #user_recv_days = []

    i = 0
    while i < len(lc_lst):
        lc_0 = lc_lst[i].strip('\n').strip(',').split(',')
        # data like:
        # <<MMK1532_start>>:2011-06-30
        # 2010-02:
        # WMH1300,1.0,1.0,[2010-01-25],38275.0,0.0,0,[],0,0,1,0,
        # 2010-03:
        # MIB1265,1.0,1.0,[2010-03-05],26650.0,0.0,0,[],0,0,1,0,
        #
        # cert4.2的格式为：
        # <<AAE0190_Start>>
        # 2010-06-08
        # BVN0514,2.0,['2010-05-18'; '2010-06-04'],66643.0,0.0,
        # BMS0877,1.0,['2010-02-16'],26175.0,0.0,
        if len(lc_0) == 1 and user_id + '_Start' in lc_0[0]:
            index_s = i + 1
            while index_s < len(lc_lst):
                lc_lst_0 = lc_lst[index_s].strip('\n').strip(',').split(',')
                if len(lc_lst_0) == 1 and lc_lst_0[0].strip(':') > month:
                    print '超出的月份为：', user_id, lc_lst_0[0].strip(':'), '\n'
                    break
                if len(lc_lst_0) == 1 and user_id + '_End' in lc_lst_0[0]:
                    break
                if len(lc_lst_0) > 1:
                    # 计算通信的天数，如果有重复，需要去掉重复的天
                    if lc_lst_0[0] not in user_lcontacts:
                        user_lcontacts.append(lc_lst_0[0])
                    # <<AAE0190_Start>>
                    # 2010-06-08
                    # BVN0514,2.0,['2010-05-18'; '2010-06-04'],66643.0,0.0,
                    # BMS0877,1.0,['2010-02-16'],26175.0,0.0,
                    # print 'test:', lc_lst_0, '\n'
                    user_cnt_send += float(lc_lst_0[1])
                    #user_cnt_recv += float(lc_lst_0[6])
                    user_send_size += float(lc_lst_0[3])
                    #user_recv_size += float(lc_lst_0[8])
                    user_send_attach += float(lc_lst_0[4])
                    #user_recv_attach += float(lc_lst_0[9])
                    for day in lc_lst_0[2].strip('[').strip(']').split(';'):
                        if len(day) == 0:
                            continue
                        if day not in user_send_days:
                            user_send_days.append(day)
                    #for day in lc_lst_0[7].strip('[').strip(']').split(';'):
                    #    if len(day) == 0:
                    #        continue
                    #    if day not in user_recv_days:
                    #        user_recv_days.append(day)
                    print user_id, 'leave_contact:', lc_lst_0[0], user_send_days, '\n'
                    index_s += 1
                    continue
                else:
                    index_s += 1
                    continue
            print user_id, month, 'lc 提取完毕..跳出循环..\n' # 没有这一步将无限循环
            break
        else:
            i += 1
            continue
    user_lc_feat.append(user_id)
    #X = len(user_send_days)
    #Y = len(user_recv_days)
    #if X + Y > 0:
    #    user_lc_feat.append(float(X - Y) / (X + Y))
    #else:
    #    user_lc_feat.append(0.0)
    user_lc_feat.append(user_cnt_send)
    #user_lc_feat.append(user_cnt_recv)
    user_lc_feat.append(user_send_size)
    #user_lc_feat.append(user_recv_size)
    user_lc_feat.append(user_send_attach)
    #user_lc_feat.append(user_recv_attach)
    user_lc_feat.append(float(len(user_send_days)))
    #user_lc_feat.append(float(len(user_recv_days)))
    #user_send_days.extend(user_recv_days)
    # [].extend()没有返回值，直接修改原列表
    #同理，对于直接修改原对象的方法而言，[].append()也没有返回值
    #user_email_days = set(user_send_days)
    #user_lc_feat.append(float(len(user_email_days)))
    print user_id, 'email_feat提取完毕...\n'
    return user_lcontacts, user_lc_feat # 12-format: user_id, cnt_send, cnt_size, cnt_s_attach, cnt_s_days

def Cal_Distance_OCEAN(user_a_ocean, user_b_ocean):
    distance_a_b = 0.0
    i = 1
    while i < len(user_a_ocean):
        distance_a_b += math.pow(user_a_ocean[i] - user_b_ocean[i], 2)
        i += 1
    distance_a_b = math.pow(distance_a_b, 0.5)
    return distance_a_b

def Cal_Distance_LDAP(user_a_ldap, user_b_ldap):
    distance_a_b = 0.0
    i = 1
    while i < len(user_a_ldap):
        if user_a_ldap[i] == user_b_ldap[i]:
            distance_a_b += math.pow(2, len(user_a_ldap) - i)
            i += 1
        else:
            distance_a_b += 0
            i += 1
    return distance_a_b


def Cal_Personality_Feat(user_a, user_lcontacts, f_ocean_lst):

    distance_ocean = 0.0
    user_a_ocean = Get_User_OCEAN(user_a, f_ocean_lst)
    for lcontact in user_lcontacts:
        lc_ocean = Get_User_OCEAN(lcontact, f_ocean_lst)
        distance_ocean += Cal_Distance_OCEAN(user_a_ocean, lc_ocean)
    user_cpb_i, user_cpb_o = CalCPBs(user_a_ocean)
    user_p_feat = []
    user_p_feat.append(user_a)
    user_p_feat.extend(user_a_ocean[1:])
    user_p_feat.append(user_cpb_i)
    user_p_feat.append(user_cpb_o)
    user_p_feat.append(distance_ocean)
    #if len(user_lcontacts) > 0:
    #    user_p_feat.append(distance_ocean / len(user_lcontacts))
    #else:
        # 默认处理方法：对于没有leave_contacts的用户，暂时先默认设置为0
     #   user_p_feat.append(0.0)
    return user_p_feat  # [user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean]

def Cal_OS_Feat(user_a, user_lcontacts, f_ldap_lst):

    distance_ldap = 0.0
    dis_ladp = 0.0
    user_a_ldap = Get_User_LDAP(user_a, f_ldap_lst)
    for lcontact in user_lcontacts:
        lc_ldap = Get_User_LDAP(lcontact, f_ldap_lst)
        dis_ladp = Cal_Distance_LDAP(user_a_ldap, lc_ldap)
        distance_ldap += dis_ladp
    #if len(user_lcontacts) == 0:
        #return dis_ladp, 0.0
    #else:
        #return dis_ladp, dis_ladp / len(user_lcontacts)
    return distance_ldap

class JS_SVM_Predictor():

    # 定义构造函数：
    # 1. 训练目录、验证目录以及测试目录的生成；
    # 2. 对应目录下，出勤率的统计以及离职用户列表的复制整理
    def __init__(self, dst_dir): # 主要功能：重要数据复制，以及月份目录创建
        # 数据与结果目录，确保存在
        self.Dst_Dir = sys.path[0]
        #self.Src_Dir = src_dir
        if os.path.exists(dst_dir) == False:
            os.mkdir(self.Dst_Dir)

        # 提取CERT5.2中分析的月份目录
        self.Leave_Users = [] # CERT5.2中离职用户
        self.Leave_Users_Time = [] # 对应于离职用户的离职时间，具体到了天
        self.Month_lst = []
        f_leave_months = open(self.Dst_Dir + '\\' + 'CERT4.2-Leave-Users_OnDay_0.9.csv', 'r')
        f_lm_lst = f_leave_months.readlines()
        f_leave_months.close()
        for line in f_lm_lst:
            # data like:
            # Laid off Users in CERT5.2 from 2009-12 to 2011-04
            # RMB1821,2010-02-09,ldap
            line_lst = line.strip('\n').strip(',').split(',')
            if len(line_lst) < 2:
                continue
            if line_lst[1][:7] not in self.Month_lst:
                self.Month_lst.append(line_lst[1][:7])
            tmp_lu = []
            tmp_lu.append(line_lst[0])
            tmp_lu.append(line_lst[1])
            self.Leave_Users.append(line_lst[0])
            self.Leave_Users_Time.append(tmp_lu)
        self.Month_lst.insert(0,'2010-01') # 补充上没有用户离职的2010-01
        print 'CERT5.2月份提取完毕：', self.Month_lst, '\n'
        #
        # 按月提取离职用户数据
        self.Leave_Users_Months = [[] for i in range(16)]
        i = 0
        while i < 16:
            month_0 = self.Month_lst[i]
            for line_lu in f_lm_lst:
                line_lst = line_lu.strip('\n').strip(',').split(',')
                if len(line_lst) < 2:
                    continue
                if line_lst[1][:7] == month_0:
                    self.Leave_Users_Months[i].append(line_lst)
            i += 1
        # 同步在对应位置写入当月离职用户信息
        j = 0
        while j < 16:
            f_leave_user_month = open(self.Dst_Dir + '\\' + self.Month_lst[j] + '\\' + self.Month_lst[j] + '_Leave_Users.csv', 'w')
            for lu_month in self.Leave_Users_Months[j]:
                for ele in lu_month:
                    f_leave_user_month.write(ele + ',')
                f_leave_user_month.write('\n')
            f_leave_user_month.close()
            print self.Month_lst[j], 'Leave Users提取写入完毕..\n'
            j += 1

        # 提取CERT4.2中所有用户的Leave_Contacts信息
        # 数据文件self.*_lst基本提供的都是原始行读入文件
        # 数据涉及LDAP/OCEAN/LC等
        # self.CERT52_LC_lst
        #
        f_LC = open(self.Dst_Dir + '\\' + 'CERT4.2_Users_LeaveContacts_EmailFeats.csv', 'r')
        self.CERT42_LC_lst = f_LC.readlines()
        f_LC.close()
        # 提取CERT52用户的LDAP信息
        f_LDAP = open(os.path.dirname(self.Dst_Dir) + '\\' + 'CERT4.2-2009-12.csv', 'r')
        self.CERT42_LDAP_lst = f_LDAP.readlines()
        f_LDAP.close()
        # 提取CERT5.2用户的OCEAN信息
        f_OCEAN = open(os.path.dirname(self.Dst_Dir) + '\\' + 'CERT4.2-psychometric.csv', 'r')
        self.CERT42_OCEAN_lst = f_OCEAN.readlines()
        f_OCEAN.close()

        # 初始化一个最初的完整1000用户的CERT42_Users
        self.CERT42_Users = []
        for line_psn in self.CERT42_OCEAN_lst:
            # employee_name,user_id,O,C,E,A,N
            # Calvin Edan Love,CEL0561,40,39,36,19,40
            line_lst = line_psn.strip('\n').strip(',').split(',')
            if line_lst[1] == 'user_id':
                continue
            else:
                self.CERT42_Users.append(line_lst[1])
        print 'CERT4.2分析月份目录构建完毕..\n'


    ####################################################################
    ####################################################################
    # CERT4.2的JS特征提取函数
    # CERT4.2用户的JS特征：
    # 1. user_id:
    # 2. OCEAN分数；
    # 3. CPB-I/CPB-O分数；
    # 4. 训练期间的出勤表现，迟到天数，早退天数，总工作天数
    # 5. 与离职员工群体的人格差异：Distance_OCEAN
    # 6. 与离职员工群体的组织差异：Distance_OS
    # 7. 与离职员工群体通信特征;
    # 7.1 Cnt_Send_Emails,
    # 7.2 Send_Size,
    # 7.3 Cnt_Send_Attach,
    # 7.4 Cnt_Send_Days,

    #
    # Extract_JS_Feat函数
    # 为每个月的工作用户提供其当月的LCE特征，且同步生成当月离职用户列表
    def Extract_JS_Feats(self, month):
        # type用于标识是训练集、验证集还是测试集
        # Extract_JS_Feats模块用于获取预测器的输入以及GroundTruth
        # 前期已经获取了CERT4.2中的self.Leave_Users与self.Leave_Users_Time
        CERT42_Users_Month_JS_Feats = []
        for user in self.CERT42_Users[:]:
            print '开始分析用户', user, '\n'
            # 开始构造该用户的JS特征
            if Get_User_LDAP(user, self.CERT42_LDAP_lst) == 'Not Found':
                print user, 'LDAP长度不标准...\n'
                continue
            else:
                print user, '首先提取用户的LC_Feat\n'
                user_lcontacts, user_lc_feat = Get_User_LC_Feat(user, self.CERT42_LC_lst, month)
                print user, '提取用户的OCEAN_Feat\n'
                user_p_feat = Cal_Personality_Feat(user, user_lcontacts, self.CERT42_OCEAN_lst)
                print user, '提取用户的OS_Feat\n'
                dis_ldap = Cal_OS_Feat(user, user_lcontacts, self.CERT42_LDAP_lst)

                # user_p_feat: [user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean]
                # user_lc_feat: # 12-format: user_id, email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days
                # user_oc_feat: dis_ldap, avg_dis_ldap
                user_js_feat = []
                user_js_feat.extend(user_p_feat)
                user_js_feat.append(dis_ldap)
                #user_js_feat.append(avg_dis_ldap)
                user_js_feat.extend(user_lc_feat[1:])
                CERT42_Users_Month_JS_Feats.append(user_js_feat)
                print user, 'Until', month, 'js feat is like: ', user_js_feat, '\n\n'

        # 特征写入
        f_JS_Feats = open(self.Dst_Dir + '\\' + month + '\\' + month + '_CERT4.2_LCE_Feats-0.1.csv', 'w')
        # 这里既然将LC当做一个整体，就不再考虑均值
        f_JS_Feats.write('user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, dis_os, email_ratio, cnt_send, cnt_s_size, cnt_s_attach, cnt_s_days\n')
        for line in CERT42_Users_Month_JS_Feats:
            for ele in line:
                f_JS_Feats.write(str(ele))
                f_JS_Feats.write(',')
            f_JS_Feats.write('\n')
        f_JS_Feats.close()
        print month, 'CERT4.2 JS Feats Write Done...\n\n'

    def Update_CERT42_Users(self, month):
        # month过后需要更新self.CERT42_Users以便于下个月继续提取LCE特征
        month_index = self.Month_lst.index(month)
        for lc in self.Leave_Users_Months[month_index]:
            self.CERT42_Users.remove(lc[0])
        print month, 'Update : CERT42_Users has Users', len(self.CERT42_Users), '\n'



#
#
# 按月提取LCE特征的主程序代码
LCE_obj = JS_SVM_Predictor(sys.path[0])

# 接下来开始按月提取LCE特征
Months_lst = ['2010-01', '2010-02','2010-03','2010-04','2010-05','2010-06','2010-07','2010-08','2010-09','2010-10','2010-11','2010-12', '2011-01', '2011-02', '2011-03', '2011-04']
# 不处理2011-05
for month in Months_lst[:]:
    LCE_obj.Extract_JS_Feats(month)
    LCE_obj.Update_CERT42_Users(month)








