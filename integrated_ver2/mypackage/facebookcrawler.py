# -*- coding: utf-8 -*-
"""
Created on Tue May  2 22:21:59 2017

@author: Paul
"""
# 載入python 套件
import requests
import datetime
import time
import pandas as pd

# 判斷response有無正常 正常 200，若無隔五秒鐘之後再試
def request_until_succeed(url):
    success = False
    while success is False:
        try: 
            req = requests.get(url)
            if req.status_code == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)
            print("Error for URL %s: %s" % (url, datetime.datetime.now()))
            print("Retrying.")

    return req
    
# 取得Facebook data
def getFacebookPageFeedData(page_id, access_token, num_statuses):

    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters
    base = "https://graph.facebook.com/v2.9"
    node = "/%s/posts" % page_id 
    fields = "/?fields=message,link,created_time,type,name,id," + \
            "comments.limit(0).summary(true),shares,reactions" + \
            ".limit(0).summary(true)"
    parameters = "&limit=%s&access_token=%s" % (num_statuses, access_token)
    url = base + node + fields + parameters

    # 取得data
    data = request_until_succeed(url).json()
    return data

# 取得該篇文章的 reactions like,love,wow,haha,sad,angry數目
def getReactionsForStatus(status_id, access_token):

    # See http://stackoverflow.com/a/37239851 for Reactions parameters
        # Reactions are only accessable at a single-post endpoint

    base = "https://graph.facebook.com/v2.6"
    node = "/%s" % status_id
    reactions = "/?fields=" \
            "reactions.type(LIKE).limit(0).summary(total_count).as(like)" \
            ",reactions.type(LOVE).limit(0).summary(total_count).as(love)" \
            ",reactions.type(WOW).limit(0).summary(total_count).as(wow)" \
            ",reactions.type(HAHA).limit(0).summary(total_count).as(haha)" \
            ",reactions.type(SAD).limit(0).summary(total_count).as(sad)" \
            ",reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
    parameters = "&access_token=%s" % access_token
    url = base + node + reactions + parameters

    # 取得data
    data = request_until_succeed(url).json()
    return data
    
def processFacebookPageFeedStatus(status, access_token):

    # 要去確認抓到的資料是否為空
    status_id = status['id']
    status_type = status['type']
    if 'message' not in status.keys():
        status_message = ''
    else:
        status_message = status['message']
    if 'name' not in status.keys():
        link_name = ''
    else:
        link_name = status['name']
    link = status_id.split('_')
    
    # 此連結可以回到該臉書上的post
    status_link = 'https://www.facebook.com/'+link[0]+'/posts/'+link[1]

    status_published = datetime.datetime.strptime(status['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    # 根據所在時區 TW +8
    status_published = status_published + datetime.timedelta(hours=8)
    status_published = status_published.strftime('%Y-%m-%d %H:%M:%S') 
    
    # 要去確認抓到的資料是否為空
    if 'reactions' not in status:
        num_reactions = 0
    else:
        num_reactions = status['reactions']['summary']['total_count']
    if 'comments' not in status:
        num_comments = 0
    else:
        num_comments = status['comments']['summary']['total_count']
    if 'shares' not in status:
        num_shares = 0
    else:
        num_shares = status['shares']['count']

    def get_num_total_reactions(reaction_type, reactions):
        if reaction_type not in reactions:
            return 0
        else:
            return reactions[reaction_type]['summary']['total_count']
    
    # 取得該篇文章的 reactions like,love,wow,haha,sad,angry數目
    reactions = getReactionsForStatus(status_id, access_token)
    
    num_loves = get_num_total_reactions('love', reactions)
    num_wows = get_num_total_reactions('wow', reactions)
    num_hahas = get_num_total_reactions('haha', reactions)
    num_sads = get_num_total_reactions('sad', reactions)
    num_angrys = get_num_total_reactions('angry', reactions)
    num_likes = get_num_total_reactions('like', reactions)

    # 回傳tuple形式的資料
    return (status_id, status_message, link_name, status_type, status_link,
            status_published, num_reactions, num_comments, num_shares,
            num_likes, num_loves, num_wows, num_hahas, num_sads, num_angrys)
            

def scrapeFacebookPageFeedStatus(page_id, access_token, limit_postnum):
    # all_statuses 用來儲存的list,先放入欄位名稱
    all_statuses = [('status_id', 'status_message', 'link_name', 'status_type', 'status_link',
            'status_published', 'num_reactions', 'num_comments', 'num_shares',
            'num_likes', 'num_loves', 'num_wows', 'num_hahas', 'num_sads', 'num_angrys')]
    
    has_next_page = True 
    num_processed = 0   # 計算處理多少post
    scrape_starttime = datetime.datetime.now()

    print("Scraping %s Facebook Page: %s\n" % (page_id, scrape_starttime))

    statuses = getFacebookPageFeedData(page_id, access_token, 100)

    #while has_next_page:
    for i in range(limit_postnum):
        if has_next_page == False:
            break
        for status in statuses['data']:

            # 確定有 reaction 再把結構化後的資料存入 all_statuses
            if 'reactions' in status:
                all_statuses.append(processFacebookPageFeedStatus(status,access_token))

            # 觀察爬取進度,每處理100篇post,就輸出時間,
            num_processed += 1
            if num_processed % 100 == 0:
                print("%s Statuses Processed: %s" % (num_processed, datetime.datetime.now()))

        # 每超過100個post就會有next,可以從next中取得下100篇, 直到沒有next
        if 'paging' in statuses.keys():
            statuses = request_until_succeed(statuses['paging']['next']).json()
        else:
            has_next_page = False

    print("\nDone!\n%s Statuses Processed in %s" % \
        (num_processed, datetime.datetime.now() - scrape_starttime))
    
    return all_statuses
    
def getFacebookCommentFeedData(status_id, access_token, num_comments):
    
    base = "https://graph.facebook.com/v2.6"
    node = "/%s/comments" % status_id
    fields = "?fields=id,message,like_count,created_time,comments,from,attachment"
    parameters = "&order=chronological&limit=%s&access_token=%s" % \
            (num_comments, access_token)
    url = base + node + fields + parameters

    # 取得data
    data = request_until_succeed(url)
    if data is None:
        return None
    else:
        return data.json()

def processFacebookComment(comment, status_id, parent_id = ''):
    
    # 確認資料欄位是否有值,並做處理
    comment_id = comment['id']
    comment_author = comment['from']['name']
    if 'message' not in comment:
        comment_message = ''
    else:
        comment_message = comment['message']
    if 'like_count' not in comment:
        comment_likes = 0 
    else:
        comment_likes = comment['like_count']
    
    if 'attachment' in comment:
        attach_tag = "[[%s]]" % comment['attachment']['type'].upper()
        if comment_message is '':
            comment_message = attach_tag
        else:
            comment_message = (comment_message+ " " +attach_tag)

    comment_published = datetime.datetime.strptime(comment['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
     # 根據所在時區 TW +8
    comment_published = comment_published + datetime.timedelta(hours=8)
    comment_published = comment_published.strftime('%Y-%m-%d %H:%M:%S')
    
    # 回傳tuple形式的資料
    return (comment_id, status_id, parent_id, comment_message, comment_author,
            comment_published, comment_likes)

def scrapeFacebookPageFeedComments(page_id, access_token, df, ifsub, limit):
    
    # all_statuses 用來儲存的list,先放入欄位名稱
    all_comments = [("comment_id", "status_id", "parent_id", "comment_message",
        "comment_author", "comment_published", "comment_likes")]

    num_processed = 0   # 計算處理多少post
    scrape_starttime = datetime.datetime.now()

    print("Scraping %s Comments From Posts: %s\n" % (page_id, scrape_starttime))
    
    post_df = df

    for post in post_df:
        if len(all_comments)>limit:
                break
        status_id = post['status_id']
        has_next_page = True

        comments = getFacebookCommentFeedData(status_id, access_token, 100)

        while has_next_page and comments is not None:
            for comment in comments['data']:
                
                all_comments.append(processFacebookComment(comment, status_id))
                if all_comments[-1][3].strip() == '[[STICKER]]' or all_comments[-1][3].strip() == '[[PHOTO]]':
                    all_comments.pop(-1)
                    
                if 'comments' in comment:
                    has_next_subpage = True

                    subcomments = getFacebookCommentFeedData(comment['id'], access_token, 100)

                    while has_next_subpage and ifsub:
                        for subcomment in subcomments['data']:
                            all_comments.append(processFacebookComment(
                                    subcomment,
                                    status_id,
                                    comment['id']))
                            if all_comments[-1][3].strip() == '[[STICKER]]' or all_comments[-1][3].strip() == '[[PHOTO]]':
                                all_comments.pop(-1)
                            
                            num_processed += 1
                            if num_processed % 100 == 0:
                                print("%s Comments Processed: %s" %
                                      (num_processed,
                                       datetime.datetime.now()))

                        if 'paging' in subcomments:
                            if 'next' in subcomments['paging']:
                                data =  request_until_succeed(subcomments['paging']['next'])
                                if data != None:
                                    subcomments = data.json()
                                else:
                                    subcomments = None
                            else:
                                has_next_subpage = False
                        else:
                            has_next_subpage = False
                          
                num_processed += 1
                if num_processed % 100 == 0:
                    print("%s Comments Processed: %s" %
                          (num_processed, datetime.datetime.now()))

            if 'paging' in comments:
                if 'next' in comments['paging']:
                    data =  request_until_succeed(comments['paging']['next'])
                    if data != None:
                        comments = data.json()
                    else:
                        comments = None
                else:
                    has_next_page = False
            else:
                has_next_page = False
                
    print("\nDone!\n%s Comments Processed in %s" %
          (num_processed, datetime.datetime.now() - scrape_starttime))
    return all_comments
    
#找出有關鍵字的貼文
def FindRelatedPost(df, keyword):
    related_post = []
    for i in range(len(df)):
        post_message = df.loc[i,'status_message']    
        link_message = df.loc[i,'link_name']
        iffind1 = post_message.find(keyword)
        iffind2 = link_message.find(keyword)
        if iffind1>0 or iffind2>0:        
            data = {'status_id': df.loc[i,'status_id'],
                    'post_message': df.loc[i,'status_message'],
                    'link_message': df.loc[i,'link_name']}
            related_post.append(data)
    print("total related post: "+str(len(related_post)))
    return related_post
#找出有關鍵字的留言   
def FindRelatedComment(all_comments, keyword):
    related_comments = []
    for i in range(len(all_comments)):        
        iffind = all_comments[i][3].find(keyword)
        if iffind>0:        
            data = {'status_id': all_comments[i][0],
                    'comments_message': all_comments[i][3],
                    }
            related_comments.append(data)
    print("total related comments: "+str(len(related_comments)))
    return related_comments
#把所有貼文轉成List
def FindAllPost(df):
    all_post = []
    for i in range(len(df)):
        data = {'status_id': df.loc[i,'status_id'],
                'post_message': df.loc[i,'status_message'],
                'link_message': df.loc[i,'link_name']}
        all_post.append(data)
    #print("all post: "+str(len(all_post)))
    return all_post