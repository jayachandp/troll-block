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
    def __init__(self, access_token, login_user):
        self.twit = Twitter(auth=OAuth(access_token.key, access_token.secret,
                                       CONSUMER_KEY, CONSUMER_SECRET))
        self.login_user = login_user
    
    def get_user(self):
        return self.login_user
    
    def block_user(self, user_id):
        pass
    
    def get_blocked_users(self):
        pass
    
    def unblock_user(self, user_id):
        pass
    
    def get_friends_ids(self):
        pass
    
    def get_friend(self, user_id):
        pass