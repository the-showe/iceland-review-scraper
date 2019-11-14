from scraper import IcelandReviewScraper
from twitter import TwitterAccount, Tweet

SITEMAP_URL = 'https://www.iceland.co.uk/sitemap_1-product.xml'


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
    twitter_account = TwitterAccount()
    product_page, review, tweet = write_new_random_review_tweet(
        twitter_account)
    print(product_page.product_image_url)
    print(tweet.text)
    twitter_account.tweet_image(product_page.product_image_url, tweet.text)
