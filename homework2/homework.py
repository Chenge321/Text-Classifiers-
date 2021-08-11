import json
import csv
import sys
import nltk
import os.path
import numpy
import math
#error checking
with open(sys.argv[1], 'r',encoding='utf-8') as f:
    data = json.loads(f.read())
(filepath, tempfilename) = os.path.split(sys.argv[1])
(filename, extension) = os.path.splitext(tempfilename)
for i in range(len(data)):
    #Check if there is doc does not have docid
    if not 'doc_id' in data[i].keys():
        raise Exception("Documents does not have doc_id") 

key_list = []
check_list = []
#Check if the doc_id is not unique
for i in range(len(data)):

    if data[i]['doc_id'] not in check_list:
        check_list.append(data[i]['doc_id'])

    
    else:
        raise Exception("The doc id is not unique")
tf_dict = {}
for element in check_list:
    tf_dict[element] = 0    
for i in range(len(data)):
    if len(data[i].keys()) <= 1:
        raise Exception("Documents does not have zones")  
for i in range(len(data)):
    for key in data[i]:
        if key not in key_list:
            key_list.append(key)
key_list.remove('doc_id')

#create tsv file
def positional_list(words,word):
    plist = []
    tf = 0
    for i in range(0,len(words)):
        if words[i] == word:
            tf +=1
            plist.append(str(i+1))
    plist.insert(0,str(tf))
    return plist,tf
dict_key = {}

for i in range(len(data)):
    s = ''
    docid = data[i]['doc_id']
    for key_name in key_list:  
        if key_name != 'doc_id' and key_name in data[i].keys():
            s = s+' '+data[i][key_name]

       
    words = nltk.word_tokenize(s.lower())
    
    words_2 = sorted(set(words),key=words.index) #remove all repeat element in words
   
    for word in words_2:
        plist,tf =  positional_list(words,word)
        plist.insert(0,str(docid))
       
       
        tf_dict[str(docid)] = tf_dict[docid]+(1+numpy.square(math.log10(tf)))
        if word in dict_key:
            dict_key[word].append(plist)    #save every word and its docid as a posting list in the dictionary
        else:
            dict_key[word] = []
            dict_key[word].append(plist)    

    tf_dict[str(docid)] = math.sqrt(tf_dict[str(docid)])
    
    sort_token = sorted(dict_key)
    s ="/"+filename+'.tsv'
    file_name = sys.argv[2]+s
    token = 'a'
    DF = 0
    postings = 'a'
    N = len(check_list)
    with open(file_name, 'w',encoding='utf-8') as f:
        #write the tsv file line by line by using elements in the dictionary
        for i in range(len(sort_token)):
            token = sort_token[i]
            IDF = N/len(dict_key[token])
            postings = dict_key[token]
            for a in postings:
                sublist = []
                for element in a:
                    sublist.append(element)
                sublist.insert(0,tf_dict[a[0]])
                sublist.insert(0,str(IDF))
                sublist.insert(0,token)
                
                tsv_w = csv.writer(f, delimiter='\t')
                tsv_w.writerow(sublist)  