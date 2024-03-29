import logging
from urllib.parse import urljoin
import requests
# from bs4 import BeautifulSoup

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',level=logging.INFO)

url = 'https://www.blockchain.com/btc/tx/79ec6ef52c0a2468787a5f671f666cf122f68aaed11a28b15b5da55c851aee75'


class Crawler:

    def __init__(self, urls=None):
        if urls is None:
            urls = []
        self.visited_urls = []
        self.urls_to_visit = urls

    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')
            try:
                self.crawl(url)
            except Exception:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)


if __name__ == '__main__':
    Crawler(urls=[url]).run()
