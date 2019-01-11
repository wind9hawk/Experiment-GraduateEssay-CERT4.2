# coding:utf-8
# 由于自己的愚笨，导致需要重新在CERT4.2数据集上复现主观检测方法；
# CERT4.2的邮件数据特征有：
# 1. 基本格式 date, user, pc, to, cc, bcc, from, size, attachment_count, content
# 2. 只记录了发送邮件的数据，因而没有activity字段，默认全部是用户的send行为；
# 3. 需要提取to/cc/bcc中的用户列表，查看是否有leave contacts，若有则计算其lce feats；

# 基本步骤：
# 1. 依据用户归档的邮件数据文件进行顺序遍历；
# 2. 依据Leave Contacts遍历，对于出现在该用户收件人列表中的用户进行统计四元特征
# 2.1： cnt_send, cnt_send_days, cnt_send_size, cnt_send_attach
# 3.计算完一个leave contact的LC特征后，保存在该用户的LCE特征中，存放在邮件目录下[user_id_LCE_Feats.csv]
# 4. 上述程序完毕后，再单独将所有用户的LCE特征汇总为一个大文件，格式如CERT5.2的一样

import os,sys

# 定义一个方便的由user_id映射到email地址的函数
# 不再分隔@符号，而是只考虑离职影响，不考虑非企业雇员通讯
def Map_User2Email(user_id, Nm_Emails):
    # Nm_Emails like ['Calvin Edan Love', 'CEL0561', 'Calvin.Edan.Love@dtaa.com']
    i = 0
    while i < len(Nm_Emails):
        if user_id == Nm_Emails[i][1]:
            return Nm_Emails[i][2]
        else:
            i += 1
    return False

# 1-2-3的运行开关
Flag_0 = False
if Flag_0:
    print '..<<从CERT4.2中提取所有用户的LCE特征>>..\n\n'
    print '1. 数据源准备\n'
    # CERT4.2的用户邮件文件目录
    Src_Dir = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2_Users_EmailRecord'
    # CERT4.2中的离职用户数据
    Leave_Path = sys.path[0] + '\\' + 'CERT4.2-Leave-Users_OnDay_0.9.csv'
    CERT42_Leave_Contacts = [] # 离职用户ID列表
    CERT42_LCD_lst = [] # 离职用户ID+离职日期
    f_leave = open(Leave_Path, 'r')
    for line_l in f_leave.readlines():
        line_lst = line_l.strip('\n').strip(',').split(',')
        if len(line_lst) < 2:
            continue
        CERT42_Leave_Contacts.append(line_lst[0])
        CERT42_LCD_lst.append(line_lst[:2])
    f_leave.close()
    print 'Leave_Contacts like', CERT42_Leave_Contacts[0], '\n'
    print 'Leave_Contacts_Days like', CERT42_LCD_lst[0], '\n'
    # CERT4.2中的User与Email的映射关系
    # ldap文件
    LDAP_Path = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2-2009-12.csv'
    # 同CERT5.2一样，CERT4.2中也是从2010-02开始出现离职
    f_ldap = open(LDAP_Path, 'r')
    # ldap格式：employee_name,user_id,email,role,business_unit,functional_unit,department,team,supervisor
    CERT42_Nm_Emails = []
    for line_ldap in f_ldap.readlines():
        line_lst = line_ldap.strip('\n').strip(',').split(',')
        if line_lst[1] == 'user_id':
            continue
        CERT42_Nm_Emails.append(line_lst[:3])
    f_ldap.close()
    print 'Nm_Emails like', CERT42_Nm_Emails[0], '\n'


    print '开始遍历循环CERT4.2用户邮件内容，生成每个用户对应的Leave Contacts Email Feats..\n'
    # 邮件名格式：AAE0190_EmailRecord.csv
    for file in os.listdir(Src_Dir)[:]:
        if 'LCE_Feats' in file:
            # 特征文件，不考虑
            continue
        user_id = file[:7]
        # 为该用户创建一个存储LCE特征的单独文件
        f_user_lce = open(Src_Dir + '\\' + user_id + '_LCE_Feats.csv', 'w')
        f_user_lce.write('LCE Feats for ' + user_id + '\n')
        # 开始读取该用户的邮件文件内容行
        f_user_emls = open(Src_Dir + '\\' + file, 'r')
        user_emls_lst = []
        for line_emls in f_user_emls.readlines():
            # emls格式：
            #  01/04/2010 08:19:15,AAE0190,PC-8915,Eugenia.Whilemina.Harrington@dtaa.com,,,August.Armando.Evans@dtaa.com,34681,0,
            line_lst = line_emls.strip('\n').strip(',').split(',')
            user_emls_lst.append(line_lst[:]) # 需要date字段记录通讯日期
        print user_id, '原始邮件读取完毕..\n'
        for i in range(3):
            print i, user_emls_lst[i], '\n'
        #
        # 接下来需要按照Leave_Contacts的顺序开始检查、计算其LCE特征
        for lcontact in CERT42_Leave_Contacts:
            # 先为所有leave contacts初始化四元特征
            # 后期过滤袋0项即可
            cnt_send = 0.0
            send_days = []
            cnt_size = 0.0
            cnt_attach = 0.0
            # 将该leave contact映射为email地址
            lc_emls = Map_User2Email(lcontact, CERT42_Nm_Emails)
            if lc_emls == False:
                print lcontact, '映射邮件名称失败..\n'
                continue
            for line_emls_0 in user_emls_lst:
                # 组合该记录的收件人列表
                # 此时格式：
                # date, user, pc, to, cc, bcc, from, size, attachment_count
                recv_lst = []
                recv_lst.extend(line_emls_0[3].split(';'))
                recv_lst.extend(line_emls_0[4].split(';'))
                recv_lst.extend(line_emls_0[5].split(';'))
                # print 'bug for: 收件人列表为：', recv_lst, '\n'
                # sys.exit()
                if lc_emls in recv_lst:
                    # 如果leave contacts在通信列表中，则记录该邮件
                    cnt_send += 1
                    cnt_attach += float(line_emls_0[8])
                    cnt_size += float(line_emls_0[7])
                    # date 格式：01/04/2010 08:19:15
                    send_days.append(line_emls_0[0][6:10] + '-' + line_emls_0[0][:2] + '-' + line_emls_0[0][3:5])
                    # print send_days, '\n'
                    # 验证通过
                    #
                else:
                    continue
            # 针对lcontact遍历完成，计算其特征即可
            # 不再求均值，而是保留size/attach和
            # 写入lcontact的信息即可
            if cnt_send == 0:
                # 对于空记录不需要记录
                continue
            f_user_lce.write(CERT42_LCD_lst[CERT42_Leave_Contacts.index(lcontact)][1] + ',')
            f_user_lce.write(lcontact + ',')
            f_user_lce.write(str(cnt_send) + ',')
            f_user_lce.write(str(send_days).replace(',', ';') + ',')
            f_user_lce.write(str(cnt_size) + ',')
            f_user_lce.write(str(cnt_attach) + '\n')
            #if cnt_send != 0:
            #    sys.exit()
            print user_id, '与Leave Contact', lcontact, '通讯分析完毕..\n'
        f_user_lce.close()


##
##
# 接下来需要将上一步得到的CERT4.2中LCE特征的文件合并成一个统一的大文件，存储到程序目录以供计算最终的ATF
Flag_1 = True
if Flag_1:
    Src_Dir = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2_Users_EmailRecord'
    f_lce = open(sys.path[0] + '\\' + 'CERT4.2_Users_LeaveContacts_EmailFeats.csv', 'w')
    for file in os.listdir(Src_Dir)[:]:
        # AAE0190_LCE_Feats.csv
        if 'LCE_Feats' not in file:
            continue
        else:
            user_id = file[:7]
            f_user_lce = open(Src_Dir + '\\' + file, 'r')
            user_lce_feats = []
            # 创建一个记录LC日期的列表
            lc_months = []
            f_lce.write('<<' + user_id + '_Start>>' + '\n')
            for line_lce in f_user_lce.readlines():
                line_lst = line_lce.strip('\n').strip(',').split(',')
                if len(line_lst) < 2:
                    continue
                # 2010-06-08,BVN0514,2.0,['2010-05-18'; '2010-06-04'],66643.0,0.0
                if line_lst[0][:7] not in lc_months:
                    lc_months.append(line_lst[0][:7])
                    f_lce.write(line_lst[0] + '\n')
                    for ele in line_lst[1:]:
                        f_lce.write(ele + ',')
                    f_lce.write('\n')
                    continue
                else:
                    for ele in line_lst[1:]:
                        f_lce.write(ele + ',')
                    f_lce.write('\n')
            f_user_lce.close()
            f_lce.write('<<' + user_id + '_End>>' + '\n')






















