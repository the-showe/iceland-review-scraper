from scraper import IcelandReviewScraper
from flask import Flask, render_template


app = Flask(__name__)

SITEMAP_URL = 'https://www.iceland.co.uk/sitemap_1-product.xml'


@app.route('/')
def random_review():
    scraper = IcelandReviewScraper(SITEMAP_URL)
    review = None
    while not review:
        product_page = scraper.get_random_product_page()
        if not product_page.has_reviews:
            continue
        review = product_page.get_random_review()
    review.star_str = "⭐" * review.num_stars
    return render_template('base.html', product_page=product_page, review=review)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
