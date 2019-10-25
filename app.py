from scraper import IcelandReviewScraper

SITEMAP_URL = 'https://www.iceland.co.uk/sitemap_1-product.xml'

if __name__ == '__main__':
    scraper = IcelandReviewScraper(SITEMAP_URL)
    review = None
    while not review:
        review = scraper.get_random_review()
    for k, v in review.as_dict().items():
        print(f'{k}: {v}')
