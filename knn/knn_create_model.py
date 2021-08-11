import json
import csv
import sys
import nltk
import os.path
import math
from pathlib import Path
#check valid input argument numbers
if len(sys.argv) != 3:
    print('Wrong number of input arguments')
    sys.exit()
#check JSON file existance
my_file = Path(sys.argv[1])
if my_file.exists():
    with open(sys.argv[1], 'r',encoding='utf-8') as f:
        data = json.loads(f.read())
else:
    print('JSON file does not exist')
    sys.exit()
#check tsv file existance 
tsvfile = Path(sys.argv[2])
if tsvfile.exists():
    a = input('The tsv file already existed. Do you want to overwrite? (Y/N)\n')
    if a.lower() == 'n':
        sys.exit()

N = len(data)
IDF_dic = {} #A dictionary stores the IDF value of terms
for i in range(len(data)):
    s_list = nltk.word_tokenize(data[i]["text"].lower())
    s_list = sorted(set(s_list),key=s_list.index)
    for term in s_list:
        if term not in IDF_dic.keys():
            IDF_dic[term] = 1
        else:
            IDF_dic[term] += 1
for term in IDF_dic.keys():
    #Calculate IDF VALUE
    IDF_dic[term] = math.log10(N/IDF_dic[term])

vector_list = [] #A list stores class, all terms and their weight of one document
for i in range(len(data)):
    tf_dic = {}
    s_list = nltk.word_tokenize(data[i]["text"].lower())
    for term in s_list:
        if term not in tf_dic.keys():
            tf_dic[term] = 1
        else:
            tf_dic[term] += 1
    for term in tf_dic.keys():
        tf_dic[term] = (1+ math.log10(tf_dic[term]))*IDF_dic[term]
    document_vector = ''
    for term in tf_dic.keys():
        document_vector += str(term)
        document_vector += ' '
        document_vector += str(tf_dic[term])
        document_vector += ' '
    vector_list.append(['vector',data[i]["category"],document_vector])
#Write the tsv file
with open(sys.argv[2], 'w',encoding='utf-8') as f:
    for term in IDF_dic.keys():
        sublist = []
        sublist.append('idf')
        sublist.append(term)
        sublist.append(IDF_dic[term])
        tsv_w = csv.writer(f, delimiter='\t')
        tsv_w.writerow(sublist)  
    for element in vector_list:
        tsv_w = csv.writer(f, delimiter='\t')
        tsv_w.writerow(element)  