# -*- coding: utf-8 -*-
"""
Created on Sun May 21 02:07:17 2017

@author: Paul
"""
import pickle
from sklearn.svm import SVC
import jieba
from gensim.models import doc2vec
from gensim import models
import numpy as np

#--------------load SVM-----------------------------------------
dumpclassifier = 'classifier1'
dumpDoc2vec = "doc2vec_model1"

with open(dumpclassifier, "rb") as fp:   # Unpickling
    machine = pickle.load(fp)

model = models.Doc2Vec.load(dumpDoc2vec)

readFilePath = "test_comments.txt"
file = open(readFilePath, 'r')

content = file.read()
print(content)
words = jieba.cut(content, cut_all=False)
content =  " ".join(words)

content_vec = model.infer_vector(content)
#content_vec = model.docvecs[0]
content_vec = np.reshape(content_vec,(1,100))
    
result_label = machine.predict(content_vec);

print(result_label)