import api
import articlecrawler
from newspaper import Article
import requests
from bs4 import BeautifulSoup



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
response = requests.get('https://www.reuters.com/news/archive/worldNews')
# parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')
# find all the links on the main page
links = soup.find_all('a')
# print the href attribute of each link
for link in links:
    print(link.get('href'))


