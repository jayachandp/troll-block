import oauth, httplib
from twitter import *

try:
    import simplejson
except ImportError:
    try:
        import json as simplejson
    except ImportError:
        try:
            from django.utils import simplejson
        except:
            raise "Requires either simplejson, Python 2.6 or django.utils!"

from django.http import *
from twitter_app.utils import *

CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
CONNECTION = httplib.HTTPSConnection(SERVER)

class Twit:
    def __init__(self, access_token, login_id, login_name, login_screen_name):
        token = oauth.OAuthToken.from_string(access_token)
        self.twit = Twitter(auth=OAuth(token.key, token.secret,
                                       CONSUMER_KEY, CONSUMER_SECRET))
        self.login_id = login_id
        self.login_name = login_name
        self.login_screen_name = login_screen_name
    
    def get_details(self):
        return (self.login_id, self.login_name, self.login_screen_name)
    
    def block_user(self, user_id):
        response = self.twit.blocks.create(user_id=user_id)
    
    def get_blocked_ids(self):
        response = self.twit.blocks.ids()
        return response.get('ids')
    
    def get_blocked_users(self):
        response = self.twit.blocks.list()
        return response.get('users')
    
    def unblock_user(self, user_id):
        response = self.twit.blocks.destroy(user_id=user_id)
    
    def get_friends_ids(self):
        pass
    
    def get_followers(self):
        response = self.twit.followers.list()
        return response.get('users')
    
    def show_user(self, user_id):
        pass