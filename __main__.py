from scraper import IcelandReviewScraper
from twitter import TwitterAccount

SITEMAP_URL = 'https://www.iceland.co.uk/sitemap_1-product.xml'


def find_random_review():
    scraper = IcelandReviewScraper(SITEMAP_URL)
    review = None
    while not review:
        product_page = scraper.get_random_product_page()
        if not product_page.has_reviews:
            continue
        review = product_page.get_random_review()
    review.star_str = "⭐" * review.num_stars
    return product_page, review


def write_review_tweet(product_page, review):
    review_parts = [product_page.product_title, review.star_str, review.text]
    if product_page.product_price != 'N/A':
        review_parts.insert(1, product_page.product_price)
    return ' - '.join(review_parts)


if __name__ == '__main__':
    twitter_account = TwitterAccount()
    previous_tweet_strings = (t.text for t in twitter_account.tweets)

    # Set up while loop to ensure review hasn't been tweeted before
    tweeted_before = True
    while tweeted_before:
        product_page, review = find_random_review()
        tweet_string = write_review_tweet(product_page, review)
        tweeted_before = tweet_string in previous_tweet_strings
    else:
        print(product_page.produce_image_url)
        print(tweet_string)
        twitter_account.tweet_image(
            product_page.product_image_url, tweet_string)
