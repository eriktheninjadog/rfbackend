import api
import articlecrawler
from newspaper import Article
import requests
from bs4 import BeautifulSoup
import constants
import os
import boto3
import time
import aisocketapi


def getanarticle():
    doit = articlecrawler.getrthkarticles()
    for i in doit:
        article = Article(i)
        article.download()
        article.parse()
        if len(article.text) > 300:
            print(article.title)
            api.create_verify_challenge(article.text)


#def getworldnews():
#getanarticle()
#ddd

response = requests.get('https://www.reuters.com/news/archive/worldNews')
soup = BeautifulSoup(response.content, 'html.parser')
links = soup.find_all('a')
link_set = set([link.get('href') for link in links if "/article/" in link.get('href')])
unique_links = list(link_set)
totaltext = ''
for link in unique_links:
    print(link)
    article = Article('https://www.reuters.com/'+link)
    article.download()
    article.parse() 
    darticle = article.title +'\n'
    sumtext = aisocketapi.ask_ai("Summarize this text into 100 words or less:\n" + article.text )
    darticle = darticle + sumtext +'\n------------------\n\n'
    os.environ["AWS_CONFIG_FILE"] = "/etc/aws/credentials"
    print("Translate To English")
    translate = boto3.client(service_name='translate', region_name='ap-southeas\
t-1', use_ssl=True)
    result = translate.translate_text(Text=darticle,
    SourceLanguageCode="en" , TargetLanguageCode="zh-TW")
    translated = result.get('TranslatedText')
    print(translated)
    totaltext = totaltext + translated
    time.sleep(60)
api.process_chinese("Daily News", "news",totaltext , constants.CWS_TYPE_IMPORT_TEXT  ,-1)

