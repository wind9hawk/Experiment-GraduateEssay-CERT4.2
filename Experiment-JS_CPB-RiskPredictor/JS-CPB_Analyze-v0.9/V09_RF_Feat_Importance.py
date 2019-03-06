# coding:utf-8
# 本模块提供一种使用随机森林实现的ATF特征重要性分析，以在实际实验前增加了解

import os,sys
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
import sklearn.preprocessing as skp
import sklearn.decomposition as skd
import numpy as np

def Cal_RF_Feat_Imporance(X_lst, Y_lst, Feat_Nms):
    x_train, x_test, y_train, y_test = train_test_split(X_lst, Y_lst, test_size=0.2, random_state=0)
    # feat_labels = df.columns[1:]
    forest = RandomForestClassifier(n_estimators=10000, random_state=5, n_jobs=-1)
    forest.fit(x_train, y_train)

    importances = forest.feature_importances_
    importances_feats = []
    i = 0
    while i < len(importances):
        tmp = []
        tmp.append(Feat_Nms[i])
        tmp.append(importances[i])
        importances_feats.append(tmp)
        i += 1
    importances_sort = sorted(importances_feats, key=lambda t:t[1], reverse=True)
    for i in range(len(importances)):
        print i, importances_sort[i], '\n'


# 小测试：train_test_split支持单类数据划分么
test_flag = False
if test_flag:
    #X = [1,1,1,1,1,0,0,0,0,0,2,3,4,2,4] # 如果是0:1， 非0:0
    #Y = [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0]
    # 对于双类数据而言，train_test_split自然是训练集与测试集中同时包含两类数据
    # [0, 4, 1, 1, 2, 2, 0, 3, 1, 1, 0, 4]
    # [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    #
    # [1, 0, 0]
    # [0, 1, 1]
    # 若对于一个蛋类数据呢？
    X = [1,2,3,4,5,1,2,4,5,7]
    Y = [0,0,0,0,0,0,0,0,0,0]
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    print x_train, '\n', y_train, '\n'
    print x_test, '\n', y_test, '\n'

Dst_Dir = sys.path[0] + '\\' + 'KMeans_OCSVM_Insiders_Predictor'
# month = '2010-09'
# 2010-08_CERT5.2_Users_GroundTruth.csv_v01.csv
# CERT5.2_ATF_0.1.csv
# CERT4.2_Leave_Static_CPB_ATF-0.1.csv
for file in os.listdir(Dst_Dir):
    if 'CERT5.2_Static_CPB_ATF-0.1.csv' in file:
        f_ATF_path = Dst_Dir + '\\' + file
    if 'CERT52_GroundTruth' in file:
        f_GT_path = Dst_Dir + '\\' + file
f_ATF = open(f_ATF_path, 'r')
f_ATF_lst = f_ATF.readlines()
f_ATF.close()
f_GT = open(f_GT_path, 'r')
f_GT_lst = f_GT.readlines()
f_GT.close()
ATF_lst = []
GT_lst = []
Feat_Nms = []
for line_atf in f_ATF_lst:
    line_lst = line_atf.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        Feat_Nms.extend(line_lst[1:])
        print len(Feat_Nms), Feat_Nms, '\n'
        # sys.exit()
        continue
    atf_tmp = []
    for ele in line_lst[1:]:
        atf_tmp.append(float(ele))
    ATF_lst.append(atf_tmp)
for line_gt in f_GT_lst:
    line_lst = line_gt.strip('\n').strip(',').split(',')
    if line_lst[0] == 'user_id':
        continue
    gt_tmp = []
    for ele in line_lst[1:]:
        gt_tmp.append(float(ele))
    GT_lst.extend(gt_tmp)

for i in range(5):
    print i, ATF_lst[i], '\n', GT_lst[i], '\n'


# 试着对原始的ATF_lst进行PCA或者MinMax
# ATF_MinMax_lst = skp.MinMaxScaler().fit_transform(ATF_lst)
#ATF_pca_lst = skd.PCA().fit_transform(ATF_lst)
#ATF_pca_MinMax = skp.MinMaxScaler().fit_transform(ATF_pca_lst)
#ATF_pca_scale = skp.scale(ATF_pca_lst)
ATF_scale = skp.scale(ATF_lst)
#ATF_scale_pca = skd.PCA().fit_transform(ATF_scale)
#print len(ATF_pca_lst[0]), '\n'
# ATF_array = np.array(ATF_MinMax_lst)
Cal_RF_Feat_Imporance(ATF_scale, GT_lst, Feat_Nms)
