import logging
from datetime import datetime
import os

from dotenv import load_dotenv

from scraper import IcelandReviewScraper
from twitter import TwitterAccount, Tweet

load_dotenv()

SITEMAP_URL = 'https://www.iceland.co.uk/sitemap_1-product.xml'

LOG_DIR_NAME = 'logs'
LOG_FILE_NAME = f'iceland_review_bot_{datetime.now():%Y%m%d_%H%M%S}.log'


class Logger(object):
    def __init__(self):
        """ Opens new logfile with timestamped name. Configures logging. """

        if not os.path.exists(LOG_DIR_NAME):
            os.mkdir(LOG_DIR_NAME)

        self.log_file_path = os.path.join(LOG_DIR_NAME, LOG_FILE_NAME)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s '
            '%(name)-12s '
            '%(levelname)-8s '
            '%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(self.log_file_path),
                logging.StreamHandler()
            ]
        )

    def get_current_log(self):
        with open(self.log_file_path, 'r') as logfile:
            return logfile.read()

    def count_warnings(self):
        logfile = self.get_current_log()
        return logfile.count('WARNING')


def find_random_review():
    scraper = IcelandReviewScraper(SITEMAP_URL)
    review = None
    while not review:
        product_page = scraper.get_random_product_page()
        if not product_page.has_reviews:
            continue
        review = product_page.get_random_review()
    return product_page, review


def write_new_random_review_tweet(twitter_account):
    # This isn't very clean, feel free to contribute a better solution
    successful = False
    while not successful:
        product_page, review = find_random_review()
        tweet = Tweet(product_page, review)
        if tweet.too_long or tweet.is_in_timeline(twitter_account):
            continue
        else:
            successful = True
    return product_page, review, tweet


if __name__ == '__main__':
    logger = Logger()
    twitter_account = TwitterAccount()
    product_page, review, tweet = write_new_random_review_tweet(
        twitter_account)
    logging.info(product_page.product_image_url)
    logging.info(tweet.text)
    twitter_account.tweet_image(product_page.product_image_url, tweet.text)
