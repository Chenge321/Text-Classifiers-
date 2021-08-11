import json
import csv
import sys
import nltk
import os.path
import numpy
import math
from pathlib import Path
#error checking
#arg = sys.argv[1]
#with open(sys.argv[1], 'r',encoding='utf-8') as f:
        #data = json.loads(f.read())

#check length of argument
if len(sys.argv) != 4:
    print('Wrong number of input arguments')
    sys.exit()

#check if JSON file exist or not
my_file = Path(sys.argv[1])
if my_file.exists():
    with open(sys.argv[1], 'r',encoding='utf-8') as f:
        data = json.loads(f.read())
else:
    print('JSON file does not exist')
    sys.exit()
#check value of k
if sys.argv[2].isdigit() == False:
    print('The value of k should be an positive integer number')
    sys.exit()
#check output file existence
outjson = Path(sys.argv[3])
if outjson.exists():
    a = input('The name of the output tsv file already existed. Do you want to overwrite? (Y/N)\n')
    if a.lower() == 'n':
        sys.exit()
def calculate_class_score(class_name,data):
    '''
    This function used to calculate mutual information for every term in the training documents.
    Return a dictionary contains the term and its score  (sorted by terms' score)
    '''
    num_doc = len(data)
    word_class = {} #The dictionary contains the number of document of each word in this class
    word_notclass = {} #The dictionary contains the number of document of each word not in this class
    doc_in_class = 0
    doc_notin_class = 0
    term_list = []
    for i in range(len(data)):
        if class_name == data[i]['category']:
            doc_in_class += 1
            s_list = nltk.word_tokenize(data[i]['text'].lower())
            s_list = list(set(s_list)) #remove repeat term
            for term in s_list:
                if term not in word_class.keys():
                    word_class[term] = 1
                else: 
                    word_class[term] += 1
        else:
            doc_notin_class += 1
            s_list = nltk.word_tokenize(data[i]['text'].lower())
            s_list = list(set(s_list)) #remove repeat term
            for term in s_list:
                if term not in word_notclass.keys():
                    word_notclass[term] = 1
                else: 
                    word_notclass[term] += 1
    #calculate mutual information for every word
    for term in word_class.keys():
        term_list.append(term)
    for term in word_notclass.keys():
        if term not in term_list:
            term_list.append(term)
    term_score = {}
    for term in term_list:
        if term in word_class.keys():
            N_1_1 = word_class[term]
        else:
            N_1_1 = 0
        if term in word_notclass.keys():
            N_1_0 = word_notclass[term]
        else:
            N_1_0 = 0
        N_0_1 = doc_in_class - N_1_1
        N_0_0 = doc_notin_class - N_1_0
        N = num_doc
        if N_1_1 == 0:
            case1 = 0
        else:
            case1 = N_1_1/N*math.log2((N*N_1_1)/((N_1_1+N_1_0)*(N_1_1+N_0_1)))
        if N_0_1 == 0:
            case2 = 0
        else:
            case2 = N_0_1/N*math.log2((N*N_0_1)/((N_0_0+N_0_1)*(N_0_1+N_1_1)))
        if N_1_0 == 0:
            case3 = 0
        else:
            case3 = N_1_0/N*math.log2((N*N_1_0)/((N_1_1+N_1_0)*(N_1_0+N_0_0)))
        if N_0_0 == 0:
            case4 = 0
        else:
            case4 = N_0_0/N*math.log2((N*N_0_0)/((N_0_0+N_0_1)*(N_0_0+N_1_0)))
        term_score[term] = case1 + case2 + case3 + case4
    #Sorted the terms by their score
    term_score = sorted(term_score.items(), key=lambda x: x[1], reverse=True)
    return term_score
#Choose the features based on their mutual information
class_name_list = []
for i in range(len(data)):
    if data[i]['category'] not in class_name_list:
        class_name_list.append(data[i]['category'])

class_feature = {} #Dictionary stores top-k features of each class
for class_name in class_name_list:
    feature_list = []
    term_score = calculate_class_score(class_name,data)
    for i in range(0,int(sys.argv[2])):
        feature_list.append(term_score[i][0])
    class_feature[class_name] = feature_list
finallist = []
#Write the new json file
with open(sys.argv[1], 'r',encoding='utf-8') as f, open(sys.argv[3], 'w',encoding='utf-8') as fw:
    data = json.loads(f.read())
    for i in range(len(data)):
        s_list = nltk.word_tokenize(data[i]['text'].lower())
        set_c = set(s_list) & set(class_feature[data[i]['category']])
        if len(set_c) > 0:
            finallist.append(data[i])
    json.dump(finallist,fw,indent=4)


