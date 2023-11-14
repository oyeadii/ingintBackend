import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class Crawler:
    def __init__(self, url, *args, **kwargs):
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}
    
    def get_links(self, url):
        crawled_links=[]
        crawled_links.append(url)
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a")
        for link in links:
            href = link.get("href")
            if href and not href.startswith("#"):
                absolute_link = urljoin(url, href)
                crawled_links.append(absolute_link)
                if len(crawled_links) > 30:
                    break
        return crawled_links
    
    def get_link_content(self, links):
        output = []
        if len(links)>30:
            links=links[:30]
        
        for link in links:
            if link.startswith(('http://', 'https://')):
                response = requests.get(link, verify = False, headers = self.headers)
                soup = BeautifulSoup(response.content, "html.parser")
                final_text = soup.get_text().strip()
                clean_text = re.sub(r'\s+', ' ', final_text)
                clean_text = re.sub(r'[%�\d\x00-\x1f]+', '', clean_text)
                output.append(clean_text)
        return output
    
    def get_all_site_content(self):
        links=self.get_links(self.url)
        content_list = self.get_link_content(links)
        all_content = " ".join([text for text in content_list])
        return all_content