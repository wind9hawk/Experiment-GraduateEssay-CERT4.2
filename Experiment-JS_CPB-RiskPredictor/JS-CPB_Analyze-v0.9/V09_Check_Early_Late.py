# coding:utf-8
# 本模块主要在进行检查反馈模块前，首先生成2010-01：2011-05的各个月份在职用户的出勤情况
# 由于CERT4.2是按时间、用户的顺序分别存放用户的Logon登录数据的，因此，我们一次遍历，生成所有月份的用户登录信息
# CERT4.2原始logon.csv数据，严格按照时间排序，即先日期，然后是登录登出行为的具体时间
# 此外，本修正的后的程序，不仅依据Team时间计算LED，还在feat中记录了同时迟到与早退的天数，以便于后续分析


# 基本算法：
# 1. 确定数据源与数据输出目录
# 2. 读入固定上下班时间
# 3. 按照月份开始以此读入、写入、关闭登录登出数据，统计迟到与早退的天数以及该月工作天数；

import os,sys

# 定义一个函数按月份提取原始logon.csv数据并存储
def Extract_Month_Logon(logon_path, dst_dir):
    # 参数说明
    # logon_path: CERT5.2文件原始登录登出文件路径
    # dst_dir：实验七的结果目录（..\PythonCode0\JS-Risks_Analyze-0.7）
    print '....<<<<确定数据源与输出目录>>>>....\n\n'
    f_Logon = open(logon_path, 'r')
    f_Logon_lst = f_Logon.readlines()
    f_Logon.close()

    Analyze_month = []
    i = 0
    while i < len(f_Logon_lst):
        line = f_Logon_lst[i].strip('\n').strip(',').split(',')
        # CERT5.2 logon.csv数据格式
        # id,date,user,pc,activity
        # {Q4D5-W4HH44UC-5188LWZK},01/02/2010 02:24:51,JBI1134,PC-0168,Logon
        if line[2] == 'user':
            i += 1
            continue
        date = line[1][6:10] + '-' + line[1][:2]
        if date not in Analyze_month:
            # 一个新月份，打开一个新文件开始写入
            Analyze_month.append(date)
            if os.path.exists(dst_dir + '\\' + date) == False:
                os.mkdir(dst_dir + '\\' + date)
            f_logon_data = open(dst_dir + '\\' + date + '\\' + date + '_logon_data.csv', 'w')
            for ele in line[1:]:
                f_logon_data.write(ele)
                f_logon_data.write(',')
            f_logon_data.write('\n')

            # 判断文件是否需要关闭？
            # 若下一行为新月份，则需要关闭文件
            # 如果是最后一行，直接关闭文件即可
            if i == len(f_Logon_lst) - 1:
                f_logon_data.close()
                print '已分析到最后一行，logon.csv按月存储结束...\n'
                break
            line_next = f_Logon_lst[i + 1].strip('\n').strip(',').split(',')
            date_next = line_next[1][6:10] + '-' + line_next[1][:2]
            if date_next not in Analyze_month:
                # 下一行为新月份数据
                f_logon_data.close()
                print date, 'logon 数据分析完毕...\n\n'
                # f_logon_data = open(dst_dir + '\\' + date_next + '\\' + date_next + '_logon_data.csv', 'w')
            i += 1
            continue
        else:
            # 文件肯定已经打开
            for ele in line[1:]:
                f_logon_data.write(ele)
                f_logon_data.write(',')
            f_logon_data.write('\n')
            i += 1
            continue

    print '分析月份列表为：\n'
    for i in range(len(Analyze_month)):
        print i, Analyze_month[i], '\n'
    return Analyze_month


# 遇到了一个新月份的登录数据

def Extract_Early_Late_Feat(analyze_month_lst, filePath, dst_dir,work_time_path):
    # 参数说明
    # analyze_month_lst: CERT4.2文件原始登录登出文件路径
    # work_time_path：自己统计的2010-01月份用户固定上下班时间
    # dst_dir：实验九的结果目录（..\PythonCode0\JS-Risks_Analyze-0.7）
    print '......<<<<<<实验系列七的用户迟到早退分析模块>>>>>>......\n\n'
    f_work_time = open(work_time_path, 'r')
    f_work_time_lst = f_work_time.readlines()
    f_work_time.close()

    Work_time_lst = []
    for line in f_work_time_lst:
        line_lst = line.strip('\n').strip(',').split(',')
        # WorkOn Time文件数据格式
        # AAB1302,WorkOn:9.0,WorkOff:19.0
        tmp_1 = []
        for ele in line_lst:
            tmp_1.append(ele.split(':')[-1])
        Work_time_lst.append(tmp_1)
    print 'Work_Time初始化完毕..\n\n'

    print '....<<<<初始化数据结构>>>>....\n\n'
    # 函数内部的全局变量，首字母大写，如User_name_lst
    # 代码全局变量，单词首字母大写，如User_Name_lst
    # 定义一个动态的月份列表，整体工作分为两部分
    # 1. 从原始的logon.csv数据中按月提取、存储到指定目录中的月份登录信息
    # 2. 循环进入月份登录信息，从中建立每个用户的出勤特征，存储

    # 注意！！
    # 为了一次遍历，便生成ID与对应的统计特征Feat，因此采用双层列表结构
    # Id层：[user_id]
    # Feat层：[feat]
    # 最后拼接即可：index: user_id, feat

    # 进入循环月份

    # 错误！
    # 由于需要考虑一天中多次登录与登出行为，我们仅关注一天中最早的登入与最晚的登出，因此
    # 补充一个当月所有天的列表，一天一天的分析用户当天所有登录登出行为
    # 若当天缺失了logon/logoff中的一项，则作为脏数据跳过，不纳入分析
    for month in analyze_month_lst:
        #file_dir = dst_dir + '\\' + month
        print 'Bug for: 当前处理月份为：', month, '\n'
        for file in os.listdir(month):
            if 'Logon' in file:
                filePath = month + '\\' + file
                break
            else:
                continue
        f_logon = open(filePath, 'r')
        f_logon_lst = f_logon.readlines()
        f_logon.close()
        # 原本考虑如果：
        # 一次遍历生成所有用户的特征，可以采用双层列表
        # 然而由于单个用户一天中存在多次登录行为，需要进一步筛选进行比较，因而转而采用两步策略：
        # 1. 建立用户的月的登录行为列表，每个用户一个列表，列表中记录当天登入时间顺序以及登出时间顺序
        # [[[logon_t_0, logon_t_1...]. [logoff_t_0, logoff_t_1...]]]
        # user_id:day:[logons, logoffs]
        logon_users = []
        users_logon_feat_lst = []
        j = 0
        while j < len(f_logon_lst):
            line = f_logon_lst[j].strip('\n').strip(',').split(',')
            # 05/01/2011 01:59:02,AHN0681,PC-9308,Logon,
            if line[1] not in logon_users:
                logon_users.append(line[1])
                j += 1
            else:
                j += 1
                continue
        print '当月登录用户列表统计完成...\n'
        f_early_late_feat = open(month + '\\' + month[-7:] + '_early_late_team_feats.csv', 'w')
        for user in logon_users[:]:
            f_early_late_feat.write(user)
            f_early_late_feat.write(',')
            # 建立该用户的当月登录登出时间列表
            user_logon_lst = []
            user_logoff_lst = []
            # 定义该用户当月的出勤特征
            user_workon_feat = [0.0 for i in range(5)]
            # 提取该用户的正常上下班时间
            j = 0
            while j < len(Work_time_lst):
                if Work_time_lst[j][0] == user:
                    user_on_time = float(Work_time_lst[j][1])
                    user_off_time = float(Work_time_lst[j][2])
                    break
                else:
                    j += 1
                    continue
            user_workon_feat[0] = user_on_time
            user_workon_feat[1] = user_off_time
            # 开始分析当月登录数据
            user_workdays = []
            j = 0
            while j < len(f_logon_lst):
                # 05/01/2011 01:59:02,AHN0681,PC-9308,Logon,
                line = f_logon_lst[j].strip('\n').strip(',').split(',')
                if line[1] == user:
                    date = line[0][6:10] + '-' + line[0][:2] + '-' + line[0][3:5]
                    if date not in user_workdays:
                        user_workdays.append(date)
                    j += 1
                    continue
                else:
                    j += 1
                    continue
            print user, date, '工作日workdays统计完毕...\n'

            # 定义保存该用户当月缺勤行为天的列表
            user_late_days = []
            user_early_days = []
            # 即提取了该月用户正常上下班的时间
            # 也有了该月用户工作日期
            # 下面则依据该用户、工作日建立登录行为列表
            for day in user_workdays:
                # 用户某一天的登录行为列表，记录的登录时间
                user_logon_day = []
                user_logoff_day = []
                j = 0
                while j < len(f_logon_lst):
                    # 05/01/2011 01:59:02,AHN0681,PC-9308,Logon,
                    line = f_logon_lst[j].strip('\n').strip(',').split(',')
                    date = line[0][6:10] + '-' + line[0][:2] + '-' + line[0][3:5]
                    if line[1] == user and date == day:
                        user_time = float(line[0][11:13]) + float(line[0][14:16]) / 60
                        if line[-1] == 'Logon':
                            user_logon_day.append(user_time)
                            j += 1
                            continue
                        else:
                            user_logoff_day.append(user_time)
                            j += 1
                            continue
                    else:
                        j += 1
                        continue
                # 当天，该用户的登录时间次数与登出时间次数一目了然
                # 从中筛选最早的登入与最晚的登出
                # print 'Error: ', user, day, '\n'
                if len(user_logon_day) == 0 or len(user_logoff_day) == 0:
                    # 当天缺失了logon，脏数据，跳过
                    continue
                user_early_logon = min(user_logon_day)
                user_late_logoff = max(user_logoff_day)
                #print '示例：'
                #print 'user_logon_day: ', user, user_logon_day, '\n'
                #print 'user_early_logon: ', user, user_early_logon, '\n'
                #print 'user_logoff_day: ', user, user_logoff_day, '\n'
                #print 'user_late_logoff: ', user, user_late_logoff, '\n'
                #
                # sys.exit()
                #
                # 然后开始比较用户当天是否迟到早退
                if user_early_logon > user_on_time:
                    # 说明迟到
                    user_workon_feat[2] += 1.0
                    if day not in user_late_days:
                        user_late_days.append(day)
                else:
                    user_workon_feat[2] += 0
                if user_late_logoff < user_off_time:
                    user_workon_feat[3] += 1
                    if day not in user_early_days:
                        user_early_days.append(day)
                else:
                    user_workon_feat[3] += 0.0

            user_workon_feat[4] = len(user_workdays)
            users_logon_feat_lst.append(user_workon_feat)

            # 需要提取同一天既有迟到又有早退的天
            user_le_days = []
            for day_l in user_late_days:
                if day_l in user_early_days and day_l not in user_le_days:
                    user_le_days.append(day_l)
            for day_e in user_early_days:
                if day_e in user_late_days and day_e not in user_le_days:
                    user_le_days.append(day_e)

            print '将结果写入...\n'
            for ele in user_workon_feat:
                f_early_late_feat.write(str(ele))
                f_early_late_feat.write(',')
            if len(user_le_days) == 0:
                f_early_late_feat.write(str(-1))
                f_early_late_feat.write('\n')
            else:
                f_early_late_feat.write(str(len(user_le_days)))
                f_early_late_feat.write(',')
                for day_0 in user_le_days:
                    f_early_late_feat.write(str(day_0))
                    f_early_late_feat.write(',')
                f_early_late_feat.write('\n')
        f_early_late_feat.close()

    return 1





print '......<<<<<<<CERT4.2用户按月出勤情况分析模块>>>>>>.......\n\n'

print '....<<<<数据源确定>>>>....\n\n'
f_Logon_Path = os.path.dirname(sys.path[0]) + '\\' + 'CERT4.2-logon.csv'
Dst_Dir = sys.path[0]
Work_Time_Path = Dst_Dir + '\\' + 'V09_CERT4.2_Users_WorkOn-Off_Time_Team.csv'


#print '....<<<<第一步：提取、存储月份用户登录数据>>>>....\n\n'
#Analyze_Month = Extract_Month_Logon(f_Logon_Path, Dst_Dir)
# 生成要分析的月份列表
Analyze_Month = []
Months_lst = ['2010-01', '2010-02','2010-03','2010-04','2010-05','2010-06','2010-07','2010-08','2010-09','2010-10','2010-11','2010-12', '2011-01', '2011-02', '2011-03', '2011-04', '2011-05']
for month in Months_lst:
    if os.path.isdir(Dst_Dir + '\\' + month) == False:
        continue
    #if '2010-01' not in month:
    #    continue
    else:
        month_dir = Dst_Dir + '\\' + month
        if month_dir not in Analyze_Month:
            # 补充的是不含路径的纯'2010-01'
            Analyze_Month.append(month)
            continue
#print Analyze_Month[-2:], '\n'
#sys.exit()
# 然后开始提取登录登出特征
Return_Value = Extract_Early_Late_Feat(Analyze_Month[:1], f_Logon_Path, Dst_Dir,Work_Time_Path)

print '....<<<<CERT5.2用户迟到早退信息提取处理完毕>>>>....\n\n'