import requests
from bs4 import BeautifulSoup
from newspaper import Article

#cnn.py


def get_top_cnn_articles(limit=20):
    """
    Get the links to the top CNN articles from their website.
    
    Args:
        limit (int): Maximum number of article links to return. Default is 10.
        
    Returns:
        list: A list of dictionaries containing title and URL of top CNN articles.
    """
    url = "https://www.cnn.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Find headline articles
        headline_cards = soup.select('.container__headline-text')
        
        for card in headline_cards:
            if len(articles) >= limit:
                break
                
            title = card.text.strip()
            link_tag = card.find_parent('a')
            
            if link_tag and 'href' in link_tag.attrs:
                link = link_tag['href']
                if not link.startswith('http'):
                    link = url + link
                    
                articles.append({'title': title, 'url': link})
        #random.shuffle(articles)
        return articles[:limit]
        
    except Exception as e:
        print(f"Error fetching CNN articles: {e}")
        return []
    
import mine_ai_dialog
import openrouter

def get_article_content(url):
    """
    Extract the body and headline of an article from a given URL using the newspaper library.
    
    Args:
        url (str): URL of the article to scrape.
        
    Returns:
        dict: A dictionary containing the article's title and text content.
    """
    try:
        
        article = Article(url)
        article.download()
        article.parse()
        api = openrouter.OpenRouterAPI()
        urtext = "\n" + article.title + "\n" + article.text
        if (len(urtext) > 2000):
            urtext = api.open_router_nova_micro_v1("Shorten this text to 2000 characters or less: " + urtext )
        text = api.open_router_claude_3_5_sonnet("You are a cantonese expert, helping with translating written english to spoken Cantonese. Only respond using Cantonese written with Traditional Chinese. No Jyutping","Translate this text to spoken Cantonese spoken daily in Hong Kong:\n" + urtext )
            
        mine_ai_dialog.text_to_mp3_and_upload(text)
        
        return {
            'title': article.title,
            'text': article.text,
            'published_date': article.publish_date,
            'top_image': article.top_image
        }
        
    except Exception as e:
        print(f"Error extracting article content from {url}: {e}")
        return {'title': None, 'text': None}


def get_random_cnn_article():
    """
    Get the top CNN articles and their content.
    
    Returns:
        list: A list of dictionaries containing article titles, URLs, and content.
    """
    articles = get_top_cnn_articles()
    random.shuffle(articles)
    article = Article(articles[0]['url'])
    article.download()
    article.parse()
    return article.text


import random
if __name__ == "__main__":
    pop = get_random_cnn_article()
    print(pop)
    articles = get_top_cnn_articles()
    random.shuffle(articles)
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   {article['url']}")
        print()
        get_article_content(article['url'])
        