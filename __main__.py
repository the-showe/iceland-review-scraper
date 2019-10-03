from bs4 import BeautifulSoup
import requests
import random
from lxml import etree
import re

SITEMAP_URL = 'https://www.iceland.co.uk/sitemap_1-product.xml'


class IcelandReviewScraper(object):
    def __init__(self, sitemap_url):
        self.sitemap_url = sitemap_url
        self.sitemap_str = requests.get(self.sitemap_url).content

    def extract_product_urls_from_sitemap(self):
        product_urls = []
        root = etree.fromstring(self.sitemap_str)
        for sitemap in root:
            children = sitemap.getchildren()
            for child in children:
                if child.tag[-3:] == 'loc':
                    product_url = child.text
                    product_urls.append(product_url)
        return product_urls

    def get_random_product_url(self):
        product_url_list = self.extract_product_urls_from_sitemap()
        return random.choice(product_url_list)

    @staticmethod
    def extract_review_list_from_product_page(product_page_soup):
        review_list_soup = product_page_soup.find('div', {'class': 'reviewList'})
        reviews = review_list_soup.find_all('div', {'class': 'feefoReview'})
        if not reviews:
            return None
        return reviews

    @staticmethod
    def extract_review_from_soup(review_soup, product_url, product_title):
        stars = review_soup.find('p', {'class': 'stars'}).find_all(
            'svg', {'class': 'icon review-star-fill svg-review-star-fill-ems'})
        submitted_text = review_soup.find('p', {'class': 'text-muted submitted'}).text
        submitted_by = re.match('^Submitted by (.*) on (.*)$', submitted_text)
        try:
            submitter = submitted_by.groups()[0]
            date = submitted_by.groups()[1]
        except AttributeError as e:
            raise AttributeError(f'{submitted_text}\n{e}')

        review = {
            'product_url': product_url,
            'product_title': product_title,
            'date': date,
            'stars': len(stars),
            'submitter': submitter,
            'text': review_soup.find_all('p')[-1].text
        }

        review['characters'] = len(review['text'])
        return review

    def get_random_review(self):
        product_url = self.get_random_product_url()
        product_page_content = requests.get(product_url).content
        product_page_soup = BeautifulSoup(product_page_content, parser='lxml',
                                          features='lxml')
        product_title = product_page_soup.find('h2', {'class': 'product-name'}).text
        reviews = self.extract_review_list_from_product_page(product_page_soup)
        if not reviews:
            return None
        review_soup = random.choice(reviews)

        review = self.extract_review_from_soup(review_soup, product_url, product_title)

        return review


if __name__ == '__main__':
    scraper = IcelandReviewScraper(SITEMAP_URL)
    review = None
    while not review:
        review = scraper.get_random_review()
    for k, v in review.items():
        print(f'{k}: {v}')
