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

    def get_random_review(self):
        product_url = self.get_random_product_url()
        product_page = ProductPage(product_url)
        if not product_page.has_reviews:
            return None

        return random.choice(product_page.reviews)


class ProductPage(object):
    def __init__(self, product_url):
        self.product_url = product_url
        self.product_page_content = requests.get(product_url).content
        self.product_page_soup = BeautifulSoup(self.product_page_content,
                                               parser='lxml',
                                               features='lxml')
        self.product_title = self.product_page_soup.find('h2', {'class': 'product-name'}).text
        self.reviews = self.extract_reviews()
        self.has_reviews = bool(self.reviews)

    def extract_reviews(self):
        review_list_soup = self.product_page_soup.find('div', {'class': 'reviewList'})
        review_soup_list = review_list_soup.find_all('div', {'class': 'feefoReview'})
        review_list = [Review(review_soup, self.product_url, self.product_title)
                       for review_soup in review_soup_list]
        self.has_reviews = bool(review_soup_list)
        return review_list


class Review(object):
    def __init__(self, review_soup, product_url, product_title):
        self.review_soup = review_soup
        self.product_url = product_url
        self.product_title = product_title
        self.as_dict = self.extract_review_from_soup

    def extract_review_from_soup(self):
        stars = self.review_soup.find('p', {'class': 'stars'}).find_all(
            'svg', {'class': 'icon review-star-fill svg-review-star-fill-ems'})
        submitted_text = self.review_soup.find('p', {'class': 'text-muted submitted'}).text
        submitted_by = re.match('^Submitted by (.*) on (.*)$', submitted_text)
        try:
            submitter = submitted_by.groups()[0]
            date = submitted_by.groups()[1]
        except AttributeError as e:
            raise AttributeError(f'{submitted_text}\n{e}')

        review = {
            'product_url': self.product_url,
            'product_title': self.product_title,
            'date': date,
            'stars': len(stars),
            'submitter': submitter,
            'text': self.review_soup.find_all('p')[-1].text
        }

        review['characters'] = len(review['text'])
        return review


if __name__ == '__main__':
    scraper = IcelandReviewScraper(SITEMAP_URL)
    review = None
    while not review:
        review = scraper.get_random_review()
    for k, v in review.as_dict().items():
        print(f'{k}: {v}')
