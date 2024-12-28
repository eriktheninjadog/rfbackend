
import requests
from bs4 import BeautifulSoup

import newspaper
from newspaper import Article


def get_all_links(url):
    try:
        
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    
        # Send a GET request to the URL
        response = requests.get(url,headers=headers)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <a> tags (which define hyperlinks)
        links = soup.find_all('a')

        # Extract the href attributes
        urls = [link.get('href') for link in links if link.get('href')]

        # Filter out non-article links (you may need to adjust this based on the website structure)
        #urls = [url for url in urls if '/5' in url]
        return urls
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

import explaintext_in_simple_cantonese

if __name__ == "__main__":
    # Define the URL you want to scrape
    url = "https://news.rthk.hk/rthk/webpageCache/services/loadModNewsShowSp2List.php?lang=zh-TW&cat=4&newsCount=60&dayShiftMode=1&archive_date="
    # Get all links from the webpage
    links = get_all_links(url)

    fullfilled = []
    for i in links:      
        article = Article(i)
        article.download()
        article.parse()
        title = article.title
        text = article.text
        if len(text) > 0:
            fullfilled.append((title,text))
            if len(fullfilled) > 10:
                break
     
    for i in fullfilled:
        title = i[0]
        text = i[1]
        try:
            explaintext_in_simple_cantonese.explain_and_render_text(title+"。\n" + text)
        except:
            print("Something went wrong but never mind that")