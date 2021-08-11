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
#check input arguments' length
if len(sys.argv) != 3:
    print('Wrong number of input arguments')
    sys.exit()

#check if tsv exist or not
tsv_file = Path(sys.argv[2])
if tsv_file.exists():
    a = input('The tsv file already existed. Do you want to overwrite? (Y/N)\n')
    if a.lower() == 'n':
        sys.exit()

#check if JSON file exist or not
my_file = Path(sys.argv[1])
if my_file.exists():
    with open(sys.argv[1], 'r',encoding='utf-8') as f:
        data = json.loads(f.read())
else:
    print('JSON file does not exist')
    sys.exit()

num_doc = len(data)
prior_dic = {} #A dictionnary stores the prior
for i in range(len(data)):

    if data[i]['category'] not in prior_dic.keys():
        prior_dic[data[i]['category']] = 1
    else:
        prior_dic[data[i]['category']] += 1
for key in prior_dic.keys():
    prior_dic[key] = (prior_dic[key]+1)/(num_doc+len(prior_dic.keys()))
likelihood_dic = {} #A dictionary stores likelihood
token_class_dic = {}
for i in range(len(data)):
    if data[i]['category'] not in token_class_dic.keys():
        token_class_dic[data[i]['category']] = len(nltk.word_tokenize(data[i]['text'].lower()))
    else:
        token_class_dic[data[i]['category']] += len(nltk.word_tokenize(data[i]['text'].lower()))
for i in range(len(data)):
    #Calaulte prior and likelihood
    s_list = []
    s_list = nltk.word_tokenize(data[i]['text'].lower())
    for term in s_list:
        if term not in likelihood_dic.keys():
            likelihood_dic[term] = []
            for class_name in prior_dic.keys():
                if class_name == data[i]['category']:
                    plist = [class_name,1]
                    likelihood_dic[term].append(plist)
                else:
                    plist = [class_name,0]
                    likelihood_dic[term].append(plist)
        else:
            for element in likelihood_dic[term]:
                if element[0] == data[i]['category']:
                    element[1] += 1
for key in likelihood_dic.keys():
    for element in likelihood_dic[key]:
        element[1] = (element[1]+1)/(token_class_dic[element[0]]+len(likelihood_dic.keys()))

with open(sys.argv[2], 'w',encoding='utf-8') as f:
        #write the tsv file line by line by using elements in the dictionary
        for key in prior_dic.keys():
            sublist = ['prior',key,prior_dic[key]]
            tsv_w = csv.writer(f, delimiter='\t')
            tsv_w.writerow(sublist)
        for key in likelihood_dic.keys(): 
            for element in likelihood_dic[key]:
              
                sublist = ['likelihood',element[0],key,element[1]]
                tsv_w = csv.writer(f, delimiter='\t')
                tsv_w.writerow(sublist)
