import re
import json
import sys
import csv
import nltk
import math
import os
from pathlib import Path

#check length of argument
if len(sys.argv) != 4:
    print('Wrong number of input arguments')
    sys.exit()
#check tsv file existance
tsvfile = Path(sys.argv[1])
if tsvfile.is_file():
    pass
else:
    print('TSV file does not exist')
    sys.exit()
#check if value of k is valid or not
if sys.argv[2].isdigit() == False:
    print('The value of k should be an positive integer number')
    sys.exit()


idf_dic = {} #A dictionary stores the idf value from model
vector_dic = {} #A dictionary stores the class and vector of each training document
classname_set = [] #A list contains all classnames
with open(sys.argv[1],encoding='UTF-8') as f:
        index = csv.reader(f,delimiter='\t')
        i = 0
        for a in index:
            if len(a) !=0 and a[0] == 'idf':
                idf_dic[a[1]] = float(a[2])
            if len(a) !=0 and a[0] == 'vector':
                classname_set.append(a[1])
                sublist = a[1]+' '+a[2]
                vector_dic[str(i)] = sublist
                i += 1
classname_set = list(set(classname_set))
my_file = Path(sys.argv[3])
if my_file.exists():
    with open(sys.argv[3], 'r',encoding='utf-8') as f:
        data = json.loads(f.read())
else:
    print('JSON file does not exist')
    sys.exit()
doc_class_dic = {} #A dictionary stores the prediction result
train_list = [] #A list contians all dictionarys of all training documents' vectors
for key in vector_dic.keys():
    vector_dic2 = {} #A dictionary stores the tf-idf value of every term in the vector
    vector_list = vector_dic[key].split(' ')
    i = 1
    while i < len(vector_list)-1:
        vector_dic2[vector_list[i]] = float(vector_list[i+1])
        i += 2
    train_norm = 0
    for key in vector_dic2.keys():
        train_norm += math.pow(vector_dic2[key],2)
    train_norm  = math.sqrt(train_norm)
    for key in vector_dic2.keys():
        vector_dic2[key] = vector_dic2[key]/train_norm
    train_list.append(vector_dic2)
for i in range(len(data)):
    a = i
    dis_dic = {} #A dictionary stores the distance between the test document with each traing document

    #calculate the vector of the test document
    tf_dic = {}
    s_list = nltk.word_tokenize(data[i]["text"].lower())
    for term in s_list:
        if term in idf_dic.keys(): #ignore the term does not have IDF value in the training model
            if term not in tf_dic.keys():
                tf_dic[term] = 1
            else:
                tf_dic[term] += 1
    for term in tf_dic.keys():
        tf_dic[term] = (1+ math.log10(tf_dic[term]))*idf_dic[term]
    test_norm = 0
    for key in tf_dic.keys():
        test_norm += math.pow(tf_dic[key],2)
    test_norm  = math.sqrt(test_norm)
    for key in tf_dic.keys():
        tf_dic[key] = tf_dic[key]/test_norm
    for key in vector_dic.keys():
        vector_dic2 = train_list[int(key)] #A dictionary stores the tf-idf value of every term in the vector
        vector_list = vector_dic[key].split(' ')

        set_c = set(vector_dic2.keys()) & set(tf_dic.keys()) #The common term in the test document and training document
        set_a = set(vector_dic2.keys()) - set_c #Terms only in test document
        set_b = set(tf_dic.keys()) - set_c #Terms only in train document
        dis = 0
        for term in set_c:
            dis += math.pow(vector_dic2[term]-tf_dic[term],2)
        for term in set_a:
            dis += math.pow(vector_dic2[term],2)
        for term in set_b:
            dis += math.pow(tf_dic[term],2)
        class_list = [vector_list[0],math.sqrt(dis)]
        dis_dic[key] = class_list
    dis_dic = sorted(dis_dic.items(), key=lambda x: x[1][1])
    top_class_list = []
    for i in range(0,int(sys.argv[2])):
        top_class_list.append(dis_dic[i][1][0])
    #Make prediction by majority voting
    predict = max(top_class_list,key=top_class_list.count)
    doc_class_dic[str(a)] = predict
#Calculate the TP/FP/FN/TN value
TP_counts = {}
FP_counts = {}
FN_counts = {}
TN_counts = {}
for class_name in classname_set:
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
for class_name in classname_set:
    #Calculate the F1 value and make it equal to 0 when precison and recall are 0
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
macro_F1 = F1_sum/len(classname_set)
precision_sum = TP_sum/(TP_sum+FP_sum)
recall_sum = TP_sum/(TP_sum+FN_sum)
micro_F1 = (2*precision_sum*recall_sum)/(precision_sum+recall_sum)
print()
print('micro_F1 is '+str(micro_F1))
print('macro_F1 is '+str(macro_F1))
        
