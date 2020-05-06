import requests
import tweepy
import os


class TwitterAccount(object):
    def __init__(self):
        auth = tweepy.OAuthHandler(os.environ['TWITTER_API_KEY'],
                                   os.environ['TWITTER_API_SECRET'])

        auth.set_access_token(os.environ['TWITTER_API_ACCESS_TOKEN'],
                              os.environ['TWITTER_API_ACCESS_TOKEN_SECRET'])

        self.api = tweepy.API(auth)
        self.account_name = 'IcelandReviews'

    @property
    def user(self):
        return self.api.get_user(self.account_name)

    @property
    def tweets(self):
        return self.user.timeline()

    def tweet(self, message):
        self.api.update_status(message)

    def tweet_image(self, url, message):
        filename = 'temp.jpg'
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as image:
            for chunk in response:
                image.write(chunk)
        try:
            self.api.update_with_media(filename, status=message)
        except tweepy.error.TweepError as e:
            # Ensure file is removed even on error
            if os.path.isfile(filename):
                os.remove(filename)
            raise e
        else:
            if os.path.isfile(filename):
                os.remove(filename)


class Tweet(object):
    def __init__(self, product_page, review):
        self.product_page = product_page
        self.review = review

    @property
    def text(self):
        review_parts = [self.product_page.product_title,
                        self.review.star_str, self.review.text]
        if self.product_page.product_price != 'N/A':
            review_parts.insert(1, self.product_page.product_price)
        text = ' - '.join(review_parts)
        return text

    @property
    def too_long(self):
        return len(self.text) > 280

    def is_in_timeline(self, twitter_account):
        return self.text in twitter_account.tweets
