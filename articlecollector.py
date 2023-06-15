import api
import articlecrawler
from newspaper import Article


def getanarticle():
    doit = articlecrawler.getrthkarticles()
    for i in doit:
        article = Article(i)
        article.download()
        article.parse()
        if len(article.text) > 200:
            print(article.title)
            exit(-1)