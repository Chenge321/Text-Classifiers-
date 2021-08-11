import re
import json
import sys
import csv
import nltk
import math
import os
from pathlib import Path

#check input arguments' length
if len(sys.argv) != 3:
    print('Wrong number of input arguments')
    sys.exit()
#check tsv file existence
tsv_file = Path(sys.argv[1])
if tsv_file.is_file():
    pass
else:
    print('TSV file does not exist')
    sys.exit()

with open(sys.argv[1],encoding='UTF-8') as f:
        prior_dic = {}
        likelihood_dic = {}
        index = csv.reader(f,delimiter='\t')
        for a in index:
            if len(a) != 0 and a[0] == 'prior':
                prior_dic[a[1]] = math.log(float(a[2]))
            if len(a) != 0 and a[0] == 'likelihood':
                plist = [a[1],math.log(float(a[3]))]
                if a[2] in likelihood_dic.keys():
                    likelihood_dic[a[2]].append(plist)
                else:
                    likelihood_dic[a[2]] = []
                    likelihood_dic[a[2]].append(plist)
doc_class_dic = {}
#check JSON file existance
my_file = Path(sys.argv[2])
if my_file.exists():
    with open(sys.argv[2], 'r',encoding='utf-8') as f:
        data = json.loads(f.read())
else:
    print('JSON file does not exist')
    sys.exit()
#To predict the class of every test document
for i in range(len(data)):
    s_list = nltk.word_tokenize(data[i]['text'].lower())
    pre_log_p = float('-inf')
    for class_name in prior_dic.keys():
        log_p = prior_dic[class_name]
        for term in s_list:
            if term in likelihood_dic.keys():
                for element in likelihood_dic[term]:
                    if element[0] == class_name:
                        log_p += element[1]
        if log_p > pre_log_p:
            doc_class_dic[str(i)] = class_name
            pre_log_p = log_p
#Calculate the TP/FP/FN/TN value
TP_counts = {}
FP_counts = {}
FN_counts = {}
TN_counts = {}
for class_name in prior_dic.keys():
    TP_counts[class_name] = 0
    FP_counts[class_name] = 0
    FN_counts[class_name] = 0
    TN_counts[class_name] = 0
for i in range(len(data)):
    if data[i]['category'] == doc_class_dic[str(i)]:
         TP_counts[data[i]['category']] += 1
         for class_name in TN_counts.keys():
             if class_name != data[i]['category']:
                 TN_counts[class_name] += 1
    else:
        FP_counts[doc_class_dic[str(i)]] += 1
        FN_counts[data[i]['category']] +=1
        for class_name in TN_counts.keys():
             if class_name != data[i]['category'] and class_name != doc_class_dic[str(i)]:
                 TN_counts[class_name] += 1
TP_sum = 0
FP_sum = 0
FN_sum = 0
F1_sum = 0
#Calculate the F1 value and make it equal to 0 when precison and recall are 0
for class_name in prior_dic.keys():
    if TP_counts[class_name] == 0 and FP_counts[class_name] == 0:
        precision = 0
        recall = 0
    else:
        precision = TP_counts[class_name]/(TP_counts[class_name]+FP_counts[class_name])
        recall = TP_counts[class_name]/(TP_counts[class_name]+FN_counts[class_name])
    TP_sum += TP_counts[class_name]
    FP_sum += FP_counts[class_name]
    FN_sum += FN_counts[class_name]
    if precision==0 and recall==0:
        F1_value = 0
    else:
        F1_value = (2*precision*recall)/(precision+recall)
    print(class_name,TP_counts[class_name],FP_counts[class_name],FN_counts[class_name],TN_counts[class_name],precision,recall,F1_value,end=" ")
    F1_sum += F1_value
macro_F1 = F1_sum/len(prior_dic.keys())
precision_sum = TP_sum/(TP_sum+FP_sum)
recall_sum = TP_sum/(TP_sum+FN_sum)
micro_F1 = (2*precision_sum*recall_sum)/(precision_sum+recall_sum)
print()
print('micro_F1 is '+str(micro_F1))
print('macro_F1 is '+str(macro_F1))








