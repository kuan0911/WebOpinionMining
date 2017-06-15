# -*- coding: utf-8 -*-
"""
Created on Wed May  3 23:52:42 2017

@author: Paul
"""
import pandas as pd

# 分析的粉絲頁的id
page_id = "ETtodaySPORTS"

app_id = "254646308275408"
app_secret = "d5728e43efda7131f226304d66ca9ce0"

access_token = app_id + "|" + app_secret

df = pd.read_pickle("facebookpost_total")
keyword = '益全'
do_crawler_post = True
limit_postnum = 10
do_crawler_comment = True


#爬所有貼文
"""
if do_crawler_post:
    all_statuses = scrapeFacebookPageFeedStatus(page_id, access_token, limit_postnum)
    df = pd.DataFrame(all_statuses[1:], columns=all_statuses[0])
    df.to_pickle("facebookpost_total")
"""
#找出具有關鍵字的貼文
related_post = FindRelatedPost(df, keyword)
#爬所選擇的貼文中所有留言
if do_crawler_comment:
    all_comments = scrapeFacebookPageFeedComments(page_id, access_token, related_post, False)
    all_comments.pop(0)
#找出具有關鍵字的留言
related_comments = FindRelatedComment(all_comments, keyword)



