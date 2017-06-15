# -*- coding: utf-8 -*-
"""
Created on Wed May 31 01:14:59 2017

@author: Paul
"""

import pandas as pd
import pickle
import jieba
import os
from gensim import models
import numpy as np
from mypackage.facebookcrawler import FindRelatedPost
from mypackage.facebookcrawler import FindAllPost
from mypackage.facebookcrawler import scrapeFacebookPageFeedStatus
from mypackage.facebookcrawler import scrapeFacebookPageFeedComments
from mypackage.SVMmultiple import svmmulticlass
from collections import Counter

relative_path = os.path.join(os.getcwd(),'dict.txt.big.txt')
jieba.set_dictionary(relative_path)

# 分析的粉絲頁的id
page_id = "sport.ltn.tw"

app_id = "254646308275408"
app_secret = "d5728e43efda7131f226304d66ca9ce0"

access_token = app_id + "|" + app_secret

df = pd.read_pickle("facebookpost_total")
keyword = '陳偉殷'
do_crawler_post = False
limit_postnum = 10  #hundred
do_crawler_comment = True
do_crawler_allcomment = False
limit_commentnum = 1000000
showdetails = True
#--------------load SVM-----------------------------------------

dumpclassifier1 = 'classifier1_high_mid'
dumpclassifier2 = 'classifier1_high_low'
dumpclassifier3 = 'classifier1_mid_low'
dumpDoc2vec = "doc2vec_model1"

with open(dumpclassifier1, "rb") as fp:   # Unpickling
    machine1 = pickle.load(fp)
with open(dumpclassifier2, "rb") as fp:   # Unpickling
    machine2 = pickle.load(fp)
with open(dumpclassifier3, "rb") as fp:   # Unpickling
    machine3 = pickle.load(fp)

model = models.Doc2Vec.load(dumpDoc2vec)
stopwordfile = 'stopwords.txt'
file = open(stopwordfile, 'r')
stopwords = []
for line in file:
    stopwords.append(line.strip('\n'))
#爬所有貼文
if do_crawler_post:
    all_statuses = scrapeFacebookPageFeedStatus(page_id, access_token, limit_postnum)
    df = pd.DataFrame(all_statuses[1:], columns=all_statuses[0])
    df.to_pickle("facebookpost_total")

#找出具有關鍵字的貼文
related_post = FindRelatedPost(df, keyword)
#爬所選擇的貼文中所有留言
if do_crawler_comment:
    all_comments = scrapeFacebookPageFeedComments(page_id, access_token, related_post, False, 10000)
    all_comments.pop(0)
#--------------save all_comments-----------------------------------------   
if do_crawler_allcomment:
    all_post = FindAllPost(df)
    all_comments2 = scrapeFacebookPageFeedComments(page_id, access_token, all_post, False,limit_commentnum)
    all_comments2.pop(0)    
    with open('all_commentssport.ltn.tw', "wb") as fp:
        pickle.dump(all_comments2,fp)

#計算正負面評價
positive = 0
mid = 0
negetive = 0
total = 0
undefine = 0
all_comments_split = []
totalvec = [0 for x in range(100)]
c = Counter()
for comment in all_comments:
    content = comment[3]
    words = list(jieba.cut(content, cut_all=False))
    words_small = list(words)
    map(str.strip('\n'), words_small)
    words_small = [x for x in words_small if x not in stopwords]
    c.update(words_small)
    content =  " ".join(words)    
    content_vec = model.infer_vector(content)
    all_comments_split.append(content)
    content_vec = np.reshape(content_vec,(1,content_vec.shape[0])) 
    totalvec = totalvec +  content_vec
    result_label = svmmulticlass(machine1,machine2,machine3,content_vec);
    if result_label == 'high':
        positive = positive + 1
        total = total + 1
    elif result_label == 'mid':
        mid = mid + 1   
        total = total + 1
    elif result_label == 'low':
        negetive = negetive + 1   
        total = total + 1
    elif result_label == 'undefine':
        undefine = undefine + 1
        total = total + 1        
    if showdetails:
        print(result_label +'  '+ comment[3])
    
n = 10
top = c.most_common(n+1)
top = [x for x in top if x[0][0]!='\n']

#-------------final result-------------
print('===========================================')
print('keyword: '+keyword)
print('saerch range from: '+df.loc[len(df)-1,'status_published'])
print('             to  : '+df.loc[0,'status_published'])
print('===========================================')
print('positive: ' + str(positive))
print('mid: ' + str(mid))
print('negetive: ' + str(negetive))
print('undefine: ' + str(undefine))
print('total: ' + str(total))
print('frequent words: ')
print(top)
print('===========================================')
