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
        request = requests.get(url, stream=True)
        if request.status_code == 200:
            with open(filename, 'wb') as image:
                for chunk in request:
                    image.write(chunk)

            self.api.update_with_media(filename, status=message)
            os.remove(filename)
        else:
            raise Exception('Could not download image, so nothing to tweet.')
