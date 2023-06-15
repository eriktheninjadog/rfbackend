from textprocessing import split_text
import praw

import dataobject
from newspaper import Article
import newspaper
import requests
from bs4 import BeautifulSoup

#
# mainly concerned with web crawling:
# Getting news, getting index pages and so on
# We are always returning the cws
#

def getarticle(url):
    if url.find('news.rthk.hk') != -1:
        return getRTHKArticle( url )
    if url.find('China_irl') != -1:
        return getRedditArticle(url)
    
    article = Article(url)
    article.download()
    article.parse()
    return dataobject.Article(article.title,article.text)

def getRTHKArticle(url):
    article = Article(url)
    article.download()
    article.parse()
    return dataobject.Article(article.title,article.text)

def getRedditArticle(url):
    reddit = praw.Reddit(client_id='GFpFjVd8PUOEW0YoSBZhdA',
                     client_secret='Hhc5OlhlnKOtMKtZ0gB60IJVtpCflg',
                     user_agent='myohmy 1.0')

    submission = reddit.submission(url=url)
    post_id = submission.id
    post = reddit.submission(id=post_id)
    txt = post.title + "\n"
    post.comments.replace_more(limit=None)
    if hasattr(post, "media_metadata"):
        image_dict = post.media_metadata
        for image_item in image_dict.values():
            largest_image = image_item['s']
            image_url = largest_image['u']        
            txt = txt + ' process image|'+image_url+' process \n'
    all_comments = post.comments.list()
    for comment in all_comments:
        txt = txt + comment.body + "\n"
    return dataobject.Article(post.title,txt)

def getreddithome():
    reddit = praw.Reddit(client_id='GFpFjVd8PUOEW0YoSBZhdA',
                     client_secret='Hhc5OlhlnKOtMKtZ0gB60IJVtpCflg',
                     user_agent='myohmy 1.0')
    chisub = reddit.subreddit("china_irl")
    txt = ''
    for p in chisub.hot(limit=100):
        txt = txt + p.title + '\n'
        txt = txt + ' process articleurl|https://www.reddit.com/'+p.permalink+' process \n'
    return dataobject.Article('REDDIT TODAY',txt)

def getrthkhome():
    txt =''
    url = 'https://news.rthk.hk/rthk/ch/latest-news.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        if (link.get('href') != None and link.get('href').find('component/k2') != -1):
            txt = txt + link.text + ' process articleurl|'+link.get('href')+' process \n'
    return dataobject.Article('RTHK TODAY',txt)

def getrthkarticles():
    all = []
    txt =''
    url = 'https://news.rthk.hk/rthk/ch/latest-news.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        if (link.get('href') != None and link.get('href').find('component/k2') != -1):
            all.append( link.get('href'))
    return all



def getlibertyhome():
    txt =''
    url = 'https://www.ltn.com.tw/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        if (link.get('href') != None and link.get('href').find('news.ltn') != -1):
            txt = txt + link.text + ' process articleurl|'+link.get('href')+' process \n'
    return dataobject.Article('LIBERTY TODAY',txt)


