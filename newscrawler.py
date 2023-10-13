import requests
from bs4 import BeautifulSoup

import random

from newspaper import Article

def gethknews():
    # Send a request to the news site's first page
    url = "https://news.rthk.hk/rthk/webpageCache/services/loadModNewsShowSp2List.php?lang=zh-TW&cat=NULL&newsCount=30&dayShiftMode=0&archive_date="
    response = requests.get(url)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <a> tags with class="article-link"
    links = soup.select('a')

    # Extract the link URLs from the <a> tags
    link_urls = [link['href'] for link in links]

    #for link in links:
    #    link.first_child()
    # Print the link URLs
    #for url in link_urls:
    #    print(url)
    total = ""

    selected_elements = random.sample(link_urls, 5)

    for link in selected_elements:
        print(link)
        response = requests.get(link)
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h2',{"class":"itemTitle"}).children
        for c in title:
            title = c
        text =soup.find_all('div',{"class":"itemBody"})
        #article = Article(link)
        #article.download()
        total += title.strip() + "\n"
        for t in text:
            total += t.text.strip() + "\n"
        total += "\n\n"
        # 
    return total


