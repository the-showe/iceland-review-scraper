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
        self.product_image_url = self.extract_product_image_url()
        self.reviews = self.extract_reviews()
        self.has_reviews = bool(self.reviews)

    def extract_reviews(self):
        review_list_soup = self.product_page_soup.find('div', {'class': 'reviewList'})
        review_soup_list = review_list_soup.find_all('div', {'class': 'feefoReview'})
        review_list = [Review(review_soup, self.product_url, self.product_title, self.product_image_url)
                       for review_soup in review_soup_list]
        self.has_reviews = bool(review_soup_list)
        return review_list

    def extract_product_image_url(self):
        img_srcset = self.product_page_soup.find('img', {'class': 'primary-image'})['srcset']
        if ',' not in img_srcset:
            return img_srcset.split(' ')[0].split('?$')[0]
        else:
            return img_srcset.split(',')[0].split('?$')[0]


class Review(object):
    def __init__(self, review_soup, product_url,
                 product_title, product_image_url):
        self.review_soup = review_soup
        self.product_url = product_url
        self.product_title = product_title
        self.product_image_url = product_image_url
        self.extract_review_from_soup()

    def extract_review_from_soup(self):
        submitted_text = self.review_soup.find('p', {'class': 'text-muted submitted'}).text
        submitted_by = re.match('^Submitted by (.*) ?on (.*)$', submitted_text)
        self.date = submitted_by.groups()[1]
        self.submitter = submitted_by.groups()[0]
        
        stars = self.review_soup.find('p', {'class': 'stars'}).find_all(
            'svg', {'class': 'icon review-star-fill svg-review-star-fill-ems'})
        self.num_stars = len(stars)

        self.text = self.review_soup.find_all('p')[-1].text
        self.characters = len(self.text)

    def as_dict(self):
        return vars(self)


if __name__ == '__main__':
    scraper = IcelandReviewScraper(SITEMAP_URL)
    review = None
    while not review:
        review = scraper.get_random_review()
    for k, v in review.as_dict().items():
        print(f'{k}: {v}')
