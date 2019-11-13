from bs4 import BeautifulSoup
import requests
import random
import re

SITEMAP_URL = 'https://www.iceland.co.uk/sitemap_1-product.xml'


class IcelandReviewScraper(object):
    def __init__(self, sitemap_url):
        self.sitemap_url = sitemap_url
        self.sitemap_str = requests.get(self.sitemap_url).content

    def extract_product_urls_from_sitemap(self):
        product_urls = []
        soup = BeautifulSoup(self.sitemap_str, features='xml')
        product_urls = [loc.text for loc in soup.find_all('loc')]
        return product_urls

    def get_random_product_page(self):
        product_url_list = self.extract_product_urls_from_sitemap()
        random_url = random.choice(product_url_list)
        return ProductPage(random_url)


class ProductPage(object):
    def __init__(self, product_url):
        self.product_url = product_url
        self._product_page_soup = self.product_page_soup
        self._reviews = self.reviews

    @property
    def product_page_soup(self):
        product_page_content = requests.get(self.product_url).content
        return BeautifulSoup(product_page_content,
                             parser='lxml',
                             features='lxml')

    @property
    def product_image_url(self):
        img_srcset = self._product_page_soup.find(
            'img', {'class': 'primary-image'})['srcset']
        if ',' not in img_srcset:
            return img_srcset.split(' ')[0].split('?$')[0]
        else:
            return img_srcset.split(',')[0].split('?$')[0]

    @property
    def product_title(self):
        return self._product_page_soup.find(
            'h2', {'class': 'product-name'}).text

    @property
    def product_price(self):
        return self._product_page_soup.find(
            'span', {'class': 'product-sales-price'}
        ).text.strip()

    @property
    def reviews(self):
        review_list_soup = self._product_page_soup.find(
            'div', {'class': 'reviewList'})
        review_soup_list = review_list_soup.find_all(
            'div', {'class': 'feefoReview'})
        self.has_reviews = bool(review_soup_list)
        review_list = [Review(review_soup)
                       for review_soup in review_soup_list]
        return review_list

    def get_random_review(self):
        return random.choice(self._reviews)


class Review(object):
    def __init__(self, review_soup):
        self._review_soup = review_soup
        self._submitted_regex = self.submitted_regex

    @property
    def submitted_regex(self):
        submitted_text = self._review_soup.find(
            'p', {'class': 'text-muted submitted'}).text
        return re.match('^Submitted by (.*) ?on (.*)$', submitted_text)

    @property
    def submitter(self):
        return self._submitted_regex.groups()[0]

    @property
    def date(self):
        return self._submitted_regex.groups()[1]

    @property
    def num_stars(self):
        stars = self._review_soup.find('p', {'class': 'stars'}).find_all(
            'svg', {'class': 'icon review-star-fill svg-review-star-fill-ems'})
        return len(stars)

    @property
    def text(self):
        return self._review_soup.find_all('p')[-1].text

    @property
    def characters(self):
        return len(self.text)

    def as_dict(self):
        return vars(self)
