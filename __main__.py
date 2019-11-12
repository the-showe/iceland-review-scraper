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


if __name__ == '__main__':
    product_page, review = find_random_review()
    review_parts = [product_page.product_title, review.star_str, review.text]
    if product_page.product_price != 'N/A':
        review_parts.insert(1, product_page.product_price)
    review_str = ' - '.join(review_parts)
    twitter_account = TwitterAccount()
    twitter_account.tweet_image(product_page.product_image_url, review_str)
