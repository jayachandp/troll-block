# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
import requests
import twitter
from twitter import *
import tweepy
from requests.auth import HTTPBasicAuth
from django.db.models import Q
from block_twitter_test import settings
import urlparse
import oauth, httplib, time, datetime
from twitter import *
from models import Blocked_List, Subscribed_List
import json

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
from django.core.urlresolvers import reverse

from twitter_app.utils import *


# Gets the tokens and establishes the connection
CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
CONNECTION = httplib.HTTPSConnection(SERVER)


def index(request):
    if "access_token" in request.session:
        return HttpResponseRedirect(reverse('home'))
    return render_to_response("index.html", '',
                              context_instance=RequestContext(request))


def logout(request):
    try:
        del request.session['access_token']
        #del request.session['unauthed_token']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('twitter_oauth_unauth'))


def home(request):
    access_token = request.session.get('access_token', None)
    if not access_token:
        return HttpResponse("You need an access token!")
    token = oauth.OAuthToken.from_string(access_token)   
    twit = Twitter(auth=OAuth(token.key, token.secret,
                CONSUMER_KEY, CONSUMER_SECRET))
    login_id = request.session.get('login_id')
    login_name = request.session.get('login_name')
    login_screen_name = request.session.get('login_screen_name')
    #login_user = twit.users.show(screen_name=twit.account.settings().get('screen_name'))
    #POST method lets you block the selected users
    if request.method == "POST":
        getids = request.POST.getlist('followers')
        blocked_ids = list()
        for id_ in getids:
            response = twit.blocks.create(user_id=id_)
            blocked_ids.append(id_)
        #saving blocked ids in db
        try:
            user_obj = Blocked_List.objects.get(user_id=login_id)
            temp_list = eval(user_obj.blocked_users)
        except:
            user_obj = Blocked_List(user_id=login_id,
                                        share='no')
        #Changed DB and included blocked list
            temp_list = list()
        for id_ in getids:
            if id_ not in temp_list:
                temp_list.append(id_)
        user_obj.blocked_users = temp_list
        user_obj.save()
    data = dict()
    blocked_ids = list()
    response = twit.blocks.ids()
    getids = response.get('ids')
    try:
        blockedListObj = Blocked_List.objects.get(user_id=login_id)
        temp_list = eval(blockedListObj.blocked_users)
        for id_ in getids:
            if id_ not in temp_list:
                temp_list.append(id_)
        blockedListObj.blocked_users = temp_list
    except:
        for id_ in getids:
            blocked_ids.append(id_)
        blockedListObj = Blocked_List(user_id=login_id,
                                        share='no',
                                        blocked_users=blocked_ids)
    blockedListObj.save()
    response = twit.followers.list()
    getids = response.get('users')
    followers = list()
    for i in range(len(getids)):
        followers.append((getids[i].get('id'),
                          getids[i].get('name'),
                          getids[i].get('screen_name'))
                        )
    data = {'followers': followers,'user':login_name}
    return render_to_response("home.html",
                              data,
                              context_instance=RequestContext(request))


def blocked_users(request):
    access_token = request.session.get('access_token', None)
    if not access_token:
        return HttpResponse("You need an access token!")
    token = oauth.OAuthToken.from_string(access_token)   
    twit = Twitter(auth=OAuth(token.key, token.secret,
                CONSUMER_KEY, CONSUMER_SECRET))
    login_id = request.session.get('login_id')
    login_name = request.session.get('login_name')
    login_screen_name = request.session.get('login_screen_name')
    #login_user = twit.users.show(screen_name=twit.account.settings().get('screen_name'))
    if request.method == "POST":
        getids = request.POST.getlist('blocked_users')
        for id_ in getids:
            response = twit.blocks.destroy(user_id=id_)
    data = dict()
    blocked_users = list()
    response = twit.blocks.list()
    getids = response.get('users')
    for i in range(len(getids)):
        blocked_users.append((getids[i].get('id'),
                          getids[i].get('name'),
                          getids[i].get('screen_name'))
                        )
    data = {'blocked_users': blocked_users,'user':login_name}
    return render_to_response("blocked_users.html", data,
                                  context_instance=RequestContext(request))


def blocked_lists(request):
    access_token = request.session.get('access_token', None)
    if not access_token:
        return HttpResponse("You need an access token!")
    token = oauth.OAuthToken.from_string(access_token)   
    twit = Twitter(auth=OAuth(token.key, token.secret,
                CONSUMER_KEY, CONSUMER_SECRET))
    login_id = request.session.get('login_id')
    login_name = request.session.get('login_name')
    login_screen_name = request.session.get('login_screen_name')
    login_user = twit.users.show(screen_name=twit.account.settings().get('screen_name'))
    if request.method == "POST":
        getids = request.POST.getlist('blocked_users') 
        user_id = int(request.POST.getlist('user_list')[0])
        try:
            user_obj = Blocked_List.objects.get(user_id=login_id)
            if not user_obj.subscribed_users == '':
                subscribed_users = eval(user_obj.subscribed_users)
            else:
                subscribed_users = list()
            if not user_obj.blocked_users == '':
                temp_list = eval(user_obj.blocked_users)
            else:
                temp_list = list()
            if user_id in subscribed_users:
                subscribed_users.remove(user_id)
                for id_ in getids:
                    response = twit.blocks.destroy(user_id=id_)
                    if id_ in temp_list:
                        temp_list.remove(int(id_))
            else:
                subscribed_users.append(user_id)
                for id_ in getids:
                    response = twit.blocks.create(user_id=id_)
                    if not int(id_) in temp_list:
                        temp_list.append(int(id_))
            user_obj.blocked_users = temp_list
            user_obj.subscribed_users = subscribed_users
        except:
            for id_ in getids:
                response = twit.blocks.create(user_id=id_)
                temp_list.append(int(id_))
            user_obj = Blocked_List(user_id=login_id, 
                                    share='no', 
                                    blocked_users=temp_list,
                                    subscribed_users=[user_id])
        user_obj.save()
    data = dict()
    blocked_data = dict()
    getids = twit.friends.ids(user_id=login_id).get('ids')
    #check the ids in db for loop
    for id_ in getids:
        try:
            user_obj = Blocked_List.objects.get(user_id=int(id_))
            friend = twit.users.show(user_id=id_)
            if (user_obj.share == 'no') and (eval(user_obj.blocked_users) != []):
                #append to data
                friend_blocks = list()
                try:
                    loggedUserBlockObj = Blocked_List.objects.get(user_id=int(login_id))
                    if int(user_obj.user_id) in eval(loggedUserBlockObj.subscribed_users):
                        alredy_subscribed = True
                    else:
                        alredy_subscribed = False
                except:
                    alredy_subscribed = False
                for blocked_id in eval(user_obj.blocked_users):
                    blocked_user = twit.users.show(user_id=blocked_id)
                    friend_blocks.append((blocked_id,
                                         blocked_user.get('name'),
                                         blocked_user.get('screen_name')))
                blocked_data[(friend.get('id'),friend.get('name'),
                      friend.get('screen_name'),str(alredy_subscribed))] = friend_blocks
        except:
            pass
    data = {'blocked_data': blocked_data,'user':login_name}
    return render_to_response("blocked_lists.html", data,
                              context_instance=RequestContext(request))