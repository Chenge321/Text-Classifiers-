import re
import json
import sys
import csv
import nltk
import math
import os
from pathlib import Path
'''
This function is used to calculate the socre of every keyword in the query for every document in the pool.
Input pool: the pool of documents are considered
      keyword_query: all keywords in the query
      score_dict: a dictionary use docid as key and its score as value
Return score_dict: after update the score of document in the dictionary
'''
def calculate_score_keyword(pool,keyword_query,score_dict):
    with open(sys.argv[1],encoding='UTF-8') as f:
        index = csv.reader(f,delimiter='\t')
        
        for a in index:
            if len(a) !=0:
                for docid in pool:
                    if a[3] == docid:
                        for keyword in keyword_query:
                            if a[0] == keyword[0]:
                                 score = math.log10(float(a[1]))*(1+math.log10(int(a[4])))/float(a[2]) #calculate score use the lnc.btn "scheme"
                                 score_dict[docid] += score
    return score_dict
'''
This function is used to calculate the socre of every phrase in the query for every document in the pool.
Input pool: the pool of documents are considered
      phrase_query: all phrases in the query
      score_dict: a dictionary use docid as key and its score as value
Return score_dict: after update the score of document in the dictionary
'''
def calculate_score_phrase(pool,phrase_query,score_dict):
    for element in phrase_query:
        posting_list = []
        with open(sys.argv[1],encoding='UTF-8') as f:
                        index = csv.reader(f,delimiter='\t')
                        for a in index:
                            if len(a) !=0:
                                sublist = []
                                
                                if a[0] == element[0] and a[3] in pool:
                                  
                                    a = calculate_score(a)
                                    for j in range(1,len(a)):
                                        
                                        sublist.append(a[j])
                                    posting_list.append(sublist)
                
                        for i in range(1,len(element)):
                            
                            check_list = []
                            with open(sys.argv[1],encoding='UTF-8') as f:
                                index = csv.reader(f,delimiter='\t')
                                for a in index:
                                    if len(a) !=0:
                                        sublist = []

                                        if a[0] == element[i]:
                                            a = calculate_score(a)
                                            for j in range(1,len(a)):
                                                
                                                sublist.append(a[j])
                                            check_list.append(sublist)
                            aa = 0
                            
                            while aa < len(posting_list):
                                
                                count_2 = 0
                                for j in range(0,len(check_list)):
                                
                                    if posting_list[aa][2] == check_list[j][2]:
                                        count_2 += 1
                                        count = 0 
                                    
                                        for k in range(4,len(posting_list[aa])):
                                            if str(int(float(posting_list[aa][k]))+i) in check_list[j][4::]:
                                                count += 1
                                                posting_list[aa][0] =  str(float(posting_list[aa][0])+float(check_list[j][0]))
                                    
                                    else:
                                        pass
                                if count_2 != 0 and count != 0:
                                    aa = aa+1
                                else:
                                    
                                    del posting_list[aa]

        for doc in posting_list:
            score_dict[doc[2]] += float(doc[0])  
    return score_dict   
'''
This function is used to calculate the socre of one spcific token in the document.
Input posting_list: The line read from tsv file
Return posting_list: after calculating the score of this token and update it in posting_list[1]
'''                   
def calculate_score(posting_list):
    score = 0
    score = math.log10(float(posting_list[1]))*(1+math.log10(int(posting_list[4])))/float(posting_list[2])
    posting_list[1] = str(score)
    return posting_list
'''
This function is used to relax and remove phrase. If one phrase has more than two words, relax it by all sub-phrases with 2 consecutive words.
If only has two words, then remove it.
Input phrase: All phrase in the query
      query_number: The list of the number of documents responding to each phrases
Return phrase: The phrase after relax/remove
'''       
def Relax_phrase(phrase,query_number):
    for i in range(0,len(query_number)):
        min_index = query_number.index(min(query_number)) #find the phrase has the minimum number of documents
        if len(phrase[min_index])<2:
            query_number[min_index] = 100000
           
        if len(phrase[min_index])>2:
          
            relax_list = []
            for i in range(0,len(phrase[min_index])-1):
                sub_list = []
                sub_list.append(phrase[min_index][i])
                sub_list.append(phrase[min_index][i+1])
                relax_list.append(sub_list)
        
            del phrase[min_index]
            for element in relax_list:
                phrase.append(element)
            return phrase
        elif len(phrase[min_index]) == 2:
            del phrase[min_index]
            return phrase
'''
This function is used to deal with input query
Input words: Input query
Return phrase_query: The phrase in the input query
       keyword_query: The keyword in the input query
'''    
def deal_token(words):

    if ':' not in words:
        query = words.split(' ')
    else:
        if words[0] !=':' and words[-1] !=':':
            query = words.split(':')
          
            alist = query[0].split(' ')
            blist = query[-1].split(' ')
            del query[0] 
            del query[-1]
            for element in alist:
                query.insert(0,element) 
            for element in blist:
                query.insert(-1,element) 
        elif words[0] !=':':
            
            query = words.split(':')
            
            alist = query[0].split(' ')
            del query[0] 
            for element in alist:
                query.insert(0,element) 
        
        elif words[-1] !=':':
            query = words.split(':')
        
            alist = query[-1].split(' ')
            del query[-1] 
            for element in alist:
                query.insert(-1,element)  

        else:
            query = words.split(':')
    #deal with the space in the input query
    i = 0
    while i < len(query):
        if query[i] == '' or query[i] ==' ':
           
            del query[i]

        else:
            i = i+1
    for i in range(0,len(query)):
        query[i] = query[i].strip()
    for i in range(0,len(query)):
        query[i] = query[i].split(" ")
    phrase_query = []
    keyword_query = []
    for element in query:
        if len(element)>1:
            phrase_query.append(element)
        elif len(element) == 1:
            keyword_query.append(element)
    return phrase_query,keyword_query
'''
This function is used to deal with phrase query (by using position list)
Input words: Phrase in the input query
Return pool: The list contain all documents that contain the input phrase
       len(number_phrase): The number of phrases
       query_number: The list of the number of documents responding to each phrases
'''  
def deal_query(query):
    query_number = []
    final_list = []
    #Find posting list of every phrases
    for element in query:
        posting_list = []
        number_phrase = []
        number_phrase.append(element)
        with open(sys.argv[1],encoding='UTF-8') as f:
                index = csv.reader(f,delimiter='\t')
                for a in index:
                    if len(a) !=0:
                        sublist = []
                        
                        if a[0] == element[0]:
                            for j in range(1,len(a)):
                                
                                sublist.append(a[j])
                            posting_list.append(sublist)
                
                for i in range(1,len(element)):
                    
                    check_list = []
                    with open(sys.argv[1],encoding='UTF-8') as f:
                        index = csv.reader(f,delimiter='\t')
                        for a in index:
                            if len(a) !=0:
                                sublist = []
                            
                                if a[0] == element[i]:
                                    for j in range(1,len(a)):
                                        
                                        sublist.append(a[j])
                                    check_list.append(sublist)
                    aa = 0
                    while aa < len(posting_list):
                    
                        count_2 = 0
                        for j in range(0,len(check_list)):
                        
                            if posting_list[aa][2] == check_list[j][2]:
                                count_2 += 1
                                count = 0 
                            
                                for k in range(4,len(posting_list[aa])):
                                    if str(int(float(posting_list[aa][k]))+i) in check_list[j][4::]:
                                        count += 1
                                        posting_list[aa][0] =  str(float(posting_list[aa][0])+float(check_list[j][0]))
                            else:
                                pass
                        if count_2 != 0 and count != 0:
                            aa = aa+1
                        else:
                            
                            del posting_list[aa]
        query_number.append(len(posting_list))                        
        final_list.append(posting_list)
        #Intersect of all positing list
        while len(final_list) >1:
            i = 0
            while i < len(final_list[0]):
                count_3 =0

                for j in range(0,len(final_list[1])):
                    if final_list[0][i][2] == final_list[1][j][2]:
                        count_3 +=1
                        final_list[0][i][0] = str(float(final_list[0][i][0])+float(final_list[1][j][0]))
                if count_3 == 0:
                    del final_list[0][i]
                else:
                    i=i+1
            del final_list[1]

    pool = []

    for element in final_list:
        for i in range(0,len(element)):
            pool.append(element[i][2])
    pool = sorted(set(pool),key=pool.index)
    return(pool,len(number_phrase),query_number)

'''
This function is used to creat pool (by using all phrases in the input query)
Input phrase_query: phrases in the input query
      k: The k number in input
Return pool: The list contain all documents that are considered
'''  

def create_pool(phrase_query,k):
    #Deal with phrases first
    if len(phrase_query) !=0:
        pool,number_phrase,query_number = deal_query(phrase_query)
        while len(pool) <5*k and number_phrase>0:
            if len(phrase_query) !=1:
                new_query = Relax_phrase(phrase_query,query_number)
                pool,number_phrase,query_number = deal_query(new_query)
            #print(len(number_phrase))
            else:
                alldoc_list = []
                with open(sys.argv[1],encoding='UTF-8') as f:
                    index = csv.reader(f,delimiter='\t')
                    for a in index:
                        if len(a) != 0:
                        
                            alldoc_list.append(a[3])
                pool = sorted(set(alldoc_list),key=alldoc_list.index)

                return pool
        return pool
    # If there are not phrases left, use all documents as pool    
    else:
        alldoc_list = []
        with open(sys.argv[1],encoding='UTF-8') as f:
            index = csv.reader(f,delimiter='\t')
            for a in index:
                if len(a) != 0:
                
                    alldoc_list.append(a[3])
        pool = sorted(set(alldoc_list),key=alldoc_list.index)
        return pool
'''
In this function, use phrases to create pool first, then calculate the score of keywords for every documents. 
Second, calculate the score of every phrases. Use score_dict to sort docid in score decreasing order
'''
def main():
    posting_list = []
    arg2 = sys.argv[2]
    #k = int(sys.argv[2])
    s = sys.argv[3]
    check_error = s
    
    ###error handling ###
    #when missing a colon
    check_error = nltk.word_tokenize(check_error)
    colon = []
    colon_count = 0
    for i in check_error:
        if i == ':':
            colon_count+=1
    if (colon_count%2) !=0:
        print('Invalid input: missing colons')
        sys.exit()

    #check if the path to tsv file is valid or not
    path = Path(sys.argv[1])
    if not path.is_file():
        print('The path to tsv file (argv[1]) is invalid')
        sys.exit()

    if not arg2.isdigit():
        print('K (argv[2]) should be positive ingeter')
        sys.exit()
    ###error handling ###
    s = s.lower()
    phrase_query,keyword_query = deal_token(s)
    score_dict = {}
    k = int(sys.argv[2])
    pool = create_pool(phrase_query,k)
    for i in range(0,len(pool)):
        score_dict[pool[i]] = 0
    score_dict = calculate_score_keyword(pool,keyword_query,score_dict) #Calculate the score of keywords for every document
    score_dict = calculate_score_phrase(pool,phrase_query,score_dict)   #Calculate the score of phrases for every document
    score_dict = sorted(score_dict.items(), key=lambda x: x[1], reverse=True) #Sort docid by score in decreasing order
    print('The number of documents that were considered is '+str(len(pool)))
    non_zero_count = 0
    for element in score_dict:
        if element[1] != 0:
            non_zero_count +=1
    print('The number of documents with non-zero score is '+ str(non_zero_count))
    count = 0
    for element in score_dict:
        if count ==k:
            break
        if element[1] != 0:
            count += 1
            print(str(element[0])+'  '+str(element[1]))

main()


