# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 19:41:42 2017

@author: Paul
"""

def svmmulticlass(SVM1, SVM2, SVM3, content_vec):
    result1 = SVM1.predict(content_vec)
    result2 = SVM2.predict(content_vec)
    result3 = SVM3.predict(content_vec)
    finallabel = ''
    if result1[0] == 1 and result2[0] == 1:
        finallabel = 'high'
    elif result1[0] == 0 and result3[0] == 1:
        finallabel = 'mid'    
    elif result2[0] == 0 and result3[0] == 0:
        finallabel = 'low'
    else:
        finallabel = 'undefine'
    #print(str(result1[0])+''+str(result2[0])+''+str(result3[0]))
    return finallabel