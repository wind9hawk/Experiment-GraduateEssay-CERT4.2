# coding:utf-8

# 本模块主要依据前期提取的CERT4.2中用户的CPB特征与Leave Contacts特征一起构建每月的攻击倾向特征ATF
# 依据1：
# CERT4.2-200912-New-26JS-0.9.csv：仅考虑其中的Team/Supervisor/OCEAN/CPB部分
# 每月目录下的[Month]_CERT4.2_JS_Feats-0.1.csv，其中邮件数量特征已经均值化（除以len(lc)）
# 为了以后计算的需要，选择'New-26JS'中的利用了OCEAN计算的CPB-I/O

# ATF 格式
# 1. OCEAN分数（5个）
# 2. OCEAN决定的CPB-I/CPB-O分数（2个）
# 3. 用户OCEAN决定的JS分数
# 4. Team的CPB影响(8个)
# 5. Supervisor的CPB影响（2个）
# 6. LeaveContacts的邮件通讯特征（9个）
# 7. 用户缺勤特征（3个）

# 面向过程模块
import os,sys

def CalCPBs(O_Score, C_Score, E_Score, A_Score, N_Score):
    #CPB_1Score = A_Score * (-0.34) + A_Score * 0.36 * (-0.40)
    #CPB_2Score = C_Score * (-0.52) + A_Score * 0.36 * (-0.41)
    # CPB-I_Self = (-0.43) * A_Score + (-0.16) * C_Score + (-0.24) * -N_Score + 0.25 * E_Score + (-0.30) * O_Score
    # CPB-O_Self = (-0.41) * A_Score + (-0.44) * C_Score + (-0.47) * -N_Score + (-0.12) * E_Score + (-0.25) * O_Score
    CPB_1Score = (-0.43) * A_Score + (-0.16) * C_Score + (-0.24) * (-1 * N_Score) + 0.25 * E_Score + (-0.30) * O_Score
    CPB_2Score = (-0.41) * A_Score + (-0.44) * C_Score + (-0.47) * (-1 * N_Score) + (-0.12) * E_Score + (-0.25) * O_Score
    return CPB_1Score, CPB_2Score

# 定义一个已知用户user_id与当前月份month计算其截止到该月份的迟到早退与工作天数的函数
def Extraxt_User_LED(user_id, month, Months_lst, dst_dir):
    # 从months列表中截止到month的文件中依次查找user_id的led并累积
    cnt_late = 0.0
    cnt_early = 0.0
    cnt_work = 0.0
    #
    for month_0 in Months_lst:
        if month_0 <= month:
            # led格式
            # UIR0043,6.5,15.5,9.0,2.0,23,-1
            # DFR0218,6.5,15.5,7.0,2.0,23,1,2010-03-02,
            f_led = open(dst_dir + '\\' + month_0 + '\\' + month_0 + '_early_late_team_feats.csv', 'r')
            for line_led in f_led.readlines():
                line_lst = line_led.strip('\n').strip(',').split(',')
                if line_lst[0] != user_id:
                    continue
                else:
                    cnt_late += float(line_lst[3])
                    cnt_early += float(line_lst[4])
                    cnt_work += float(line_lst[5])
                    #if user_id == 'CEL0561':
                    #    print month_0, user_id, line_lst[3], line_lst[4], line_lst[5], '\n'
                    break
            f_led.close()
            continue
        else:
            continue
    #
    return cnt_late, cnt_early, cnt_work

print '....<<<<由CPBs与LCE特征共同构建ATF>>>>....\n\n'

print '..<<数据准备>>..\n'
Months_lst = ['2010-01', '2010-02','2010-03','2010-04','2010-05','2010-06','2010-07','2010-08','2010-09','2010-10','2010-11','2010-12', '2011-01', '2011-02', '2011-03', '2011-04', '2011-05']
Dst_Dir = sys.path[0]
f_CPBs = open(Dst_Dir + '\\' + 'CERT4.2-2009-12-New-26JS.csv', 'r')
f_CPBs_lst = f_CPBs.readlines()
f_CPBs.close()
CPBs_Users = []
CPBs_Feats = []
for line_cpb in f_CPBs_lst:
    line_lst = line_cpb.strip('\n').strip(',').split(',')
    # user_id,O_Score,C_Score,E_Score,A_Score,N_Score,Team_CPB-I-mean,Team_CPB-O-mean,Users-less-mean-A,Users-less-mean-A and C,Users-less-mean-C,Users-High-mean-N,Team_CPB-I-median,Team_CPB-O-median,No-JobState-in-Team,Dpt-CPB-I-mean,Dpt_CPB-O-mean,Dpt-Less-A-mean,Dpt-Less-AC-mean,Dpt-less-C-mean,Dpt-High-N-mean,Dpt_CPB-I-median,Dpt_CPB-O-median,No-JobState-in-Dpt,Job State,Leader_CPB-I,Leader_CPB-O
    # MMK1532,17.0,17.0,16.0,22.0,28.0,-13.761999999999999,-24.254666666666665,16,7,12,16,-14.555000000000001,-25.135,0,-13.22647435897436,-23.644999999999996,88,38,58,90,-13.729999999999999,-23.83,1,18,-4.79,-10.23,
    # cert4.2数据示例
    # user_id,O_Score,C_Score,E_Score,A_Score,N_Score,Team_CPB-I-mean,Team_CPB-O-mean,Users-less-mean-A,Users-less-mean-A and C,Users-less-mean-C,Users-High-mean-N,Team_CPB-I-median,Team_CPB-O-median,No-JobState-in-Team,Dpt-CPB-I-mean,Dpt_CPB-O-mean,Dpt-Less-A-mean,Dpt-Less-AC-mean,Dpt-less-C-mean,Dpt-High-N-mean,Dpt_CPB-I-median,Dpt_CPB-O-median,No-JobState-in-Dpt,Job State,Leader_CPB-I,Leader_CPB-O
    if line_lst[0] == 'user_id':
        # print line_lst[1:14], '\n'
        # 验证[1:14]正确
        # CPB需要重新计算
        continue
    CPBs_Users.append(line_lst[0])
    cpb_i, cpb_o = CalCPBs(float(line_lst[1]), float(line_lst[2]), float(line_lst[3]), float(line_lst[4]), float(line_lst[5]))
    cpb_tmp = line_lst[1:13] # 如果考虑Team中的未干满2010-01:2011-05的用户，就是[1:14]，这里选择使用[1:13]先不考虑
    cpb_tmp.insert(5, cpb_i) # ocean后插入新的cpb-i
    cpb_tmp.insert(6, cpb_o) # ocean cpb-i后插入新的cpb-o
    # 计算新的JS分数
    # js: 0.31 * A + 0.22 * C - 0.23 * N + 0.08 * E + 0.08 * O
    js_score = 0.08 * float(line_lst[1]) + 0.22 * float(line_lst[2]) + 0.08 * float(line_lst[3]) + 0.31 * float(line_lst[4]) - 0.23 * float(line_lst[5])
    cpb_tmp.insert(7, js_score)
    cpb_tmp.extend(line_lst[-2:]) # supervisor cpbs
    CPBs_Feats.append(cpb_tmp)
    print line_lst[0], 'new 26JS feat is ', cpb_tmp, '\n'

print '..<<开始逐个月份检查、生成ATF>>..\n'
for file in os.listdir(Dst_Dir):
    if os.path.isdir(Dst_Dir + '\\' + file) is True and '-' in file: #不分析.idea目录
        month_path = Dst_Dir + '\\' + file
        # 在该目录下找这个文件CERT5.2_Month_AvgLC_JS_Feats_v01.csv
        lce_feat_path = month_path + '\\' + file + '_CERT4.2_LCE_Feats-0.1.csv'
        if os.path.exists(lce_feat_path) == False:
            print file, '不存在Leave Contacts特征，跳过..\n' # 跳过了cert4.2的2011-05
            continue
        else:
            # 存在Leave Contacts特征，开始合并
            lce_users = []
            lce_feats = []
            f_LCE = open(lce_feat_path, 'r')
            f_LCE_lst = f_LCE.readlines()
            f_LCE.close()
            for line_lce in f_LCE_lst:
                line_lst = line_lce.strip('\n').strip(',').split(',')
                # user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean, dis_os, avg_dis_os, cnt_late_days, cnt_early_days, month_work_days, email_ratio, cnt_send/recv, cnt_s/r_size, cnt_s/r_attach, cnt_s/r_days, cnt_email_days
                # MMK1532,17.0,17.0,16.0,22.0,28.0,-10.648,-12.0872,0.0,0.0,0.0,0.0,10.0,6.0,20.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                # cert4.2 LCE
                # user_id, o, c, e, a, n, cpb-i, cpb-o, dis_ocean, avg_dis_ocean, dis_os, avg_dis_os, cnt_send, cnt_s_size, cnt_s_attach, cnt_s_days
                if line_lst[0] == 'user_id':
                    continue
                else:
                    lce_users.append(line_lst[0])
                    lce_tmp = []
                    lce_tmp.extend(line_lst[8:])
                    #lce_tmp.extend(line_lst[15:])
                    #lce_tmp.extend(line_lst[12:15]) #故意把累积LED特征放在了最后
                    # 5,6,7
                    # 这里只需要获得该用户的累积LED特征即可
                    cnt_late, cnt_early, cnt_work = Extraxt_User_LED(line_lst[0], file, Months_lst, Dst_Dir)
                    #if file == '2010-03':
                    #    print line_lst[0], cnt_late, cnt_early, cnt_work, '\n'
                    #    sys.exit()
                    lce_tmp.append(cnt_late)
                    lce_tmp.append(cnt_early)
                    lce_tmp.append(cnt_work)
                    lce_feats.append(lce_tmp)

            print lce_feat_path, '内容读取完毕...\n'

            atf_lst = []
            i = 0
            while i < len(lce_users):
                if lce_users[i] in CPBs_Users:
                    user_index = CPBs_Users.index(lce_users[i])
                    atf_tmp = []
                    atf_tmp.append(lce_users[i])
                    atf_tmp.extend(CPBs_Feats[user_index])
                    atf_tmp.extend(lce_feats[i])
                    atf_lst.append(atf_tmp)
                    i += 1
                    continue
                else:
                    print lce_feats[i], 'Lost CPBs but with LCE..\n'
                    i += 1
                    continue
            f_atf_path = month_path + '\\' + 'CERT4.2_Leave_ATF_0.1.csv'
            f_atf = open(f_atf_path, 'w')
            f_atf.write('user_id' + ',')
            # 首先写入标签
            fragments = []
            fragments.extend(['O_Score', 'C_Score', 'E_Score', 'A_Score', 'N_Score'])
            fragments.extend(['CPB-I', 'CPB-O', 'JS_Score'])
            fragments.extend(['Team_CPB-I-mean', 'Team_CPB-O-mean', 'Users-less-mean-A', 'Users-less-mean-A and C', 'Users-less-mean-C', 'Users-High-mean-N', 'Team_CPB-I-median', 'Team_CPB-O-median'])
            fragments.extend(['leader-CPB-I', 'leader-CPB-O'])
            fragments.extend(['dis_ocean',  'dis_os',   'cnt_send', 'cnt_send_size', 'cnt_send_attach', 'cnt_send_days', 'cnt_email_days'])
            fragments.extend(['cnt_late_days', 'cnt_early_days', 'month_work_days'])
            for ele in fragments:
                f_atf.write(ele + ',')
            f_atf.write('\n')
            for line_atf in atf_lst:
                for ele in line_atf:
                    f_atf.write(str(ele) + ',')
                f_atf.write('\n')
            f_atf.close()
            print file, 'ATF特征写入完毕..\n'


















