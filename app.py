from scraper import IcelandReviewScraper
from flask import Flask


app = Flask(__name__)

SITEMAP_URL = 'https://www.iceland.co.uk/sitemap_1-product.xml'


@app.route('/')
def random_review():
    scraper = IcelandReviewScraper(SITEMAP_URL)
    review = None
    while not review:
        review = scraper.get_random_review()
    return '<br/>'.join(f'{k}: {v}' for k, v in review.as_dict().items())

if __name__ == '__main__':
    app.run()
