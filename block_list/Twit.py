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
    
    def __init__(self, request):
        access_token = request.session.get('access_token', None)
        token = oauth.OAuthToken.from_string(access_token)
        self.twit = Twitter(auth=OAuth(token.key, token.secret,
                                       CONSUMER_KEY, CONSUMER_SECRET))
        self.login_id = request.session.get('login_id')
        self.login_name = request.session.get('login_name')
        self.login_screen_name = request.session.get('login_screen_name')
    
    def get_id(self):
        return self.login_id
    
    def get_name(self):
        return self.login_name
    
    def get_screen_name(self):
        return self.login_screen_name
    
    def show_user(self, user_id):
        return self.twit.users.show(user_id=user_id)
    
    def block_user(self, user_id):
        response = self.twit.blocks.create(user_id=user_id)
    
    def get_blocked_ids(self):
        response = self.twit.blocks.ids()
        data_list = response.get('ids')
        next_cursor = response.get('next_cursor')
        while next_cursor != 0:
            response = self.twit.blocks.ids(cursor=next_cursor)
            next_cursor = response.get('next_cursor')
            data_list = data_list + response.get('ids')
            if next_cursor == 0:
                break
        return data_list
    
    def get_blocked_users(self):
        response = self.twit.blocks.list()
        data_list = response.get('users')
        next_cursor = response.get('next_cursor')
        while next_cursor != 0:
            response = self.twit.blocks.list(cursor=next_cursor)
            next_cursor = response.get('next_cursor')
            data_list = data_list + response.get('users')
            if next_cursor == 0:
                break
        return data_list
    
    def unblock_user(self, user_id):
        response = self.twit.blocks.destroy(user_id=user_id)
    
    def get_friends(self):
        response = self.twit.friends.list(user_id=self.login_id)
        data_list = response.get('users')
        next_cursor = response.get('next_cursor')
        while next_cursor != 0:
            response = self.twit.friends.list(user_id=self.login_id,
                                              cursor=next_cursor)
            next_cursor = response.get('next_cursor')
            data_list = data_list + response.get('users')
            if next_cursor == 0:
                break
        return data_list
    
    def get_friends_ids(self):
        response = self.twit.friends.ids(user_id=self.login_id)
        data_list = response.get('ids')
        next_cursor = response.get('next_cursor')
        while next_cursor != 0:
            response = self.twit.friends.ids(user_id=self.login_id,
                                              cursor=next_cursor)
            next_cursor = response.get('next_cursor')
            data_list = data_list + response.get('ids')
            if next_cursor == 0:
                break
        return data_list
    
    def get_followers(self):
        response = self.twit.followers.list()
        next_cursor = response.get('next_cursor')
        data_list = response.get('users')
        while next_cursor != 0:
            response = self.twit.followers.list(cursor=next_cursor)
            next_cursor = response.get('next_cursor')
            data_list = data_list + response.get('users')
            if next_cursor == 0:
                break
        return data_list
