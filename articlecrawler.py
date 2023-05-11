from textprocessing import split_text
from textprocessing import convert_to_traditional
import praw

from newspaper import Article
import newspaper
import requests
from bs4 import BeautifulSoup


#
# mainly concerned with web crawling:
# Getting news, getting index pages and so on
# We are always returning the cws
#
#



def getarticle(url):
    if url.find('news.rthk.hk') != -1:
        return getRTHKArticle( url )
    if url.find('China_irl') != -1:
        return getRedditArticle(url)
    
    article = Article(url)
    article.download()
    article.parse()
    return [split_text(article.title),split_text(article.text)]


def getRTHKArticle(url):
    article = Article(url)
    article.download()
    article.parse()
    return [split_text(article.title),split_text(article.text)]


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
    txt = convert_to_traditional(txt)
    return [split_text(post.title),split_text(txt)] 
