# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse
from models import Blocked_List
from Twit import Twit


def index(request):
    if "access_token" in request.session:
        return HttpResponseRedirect(reverse('home'))
    return render_to_response("index.html", '',
                              context_instance=RequestContext(request))


def logout(request):
    try:
        del request.session['access_token']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('twitter_oauth_unauth'))


def home(request):
    if "access_token" in request.session:
        twitr = Twit(request)
        if request.method == "POST":
            getids = request.POST.getlist('followers')
            blocked_ids = list()
            for id_ in getids:
                twitr.block_user(id_)
                blocked_ids.append(id_)
            #saving blocked ids in db
            try:
                user_obj = Blocked_List.objects.get(user_id=twitr.login_id)
                temp_list = eval(user_obj.blocked_users)
            except:
                user_obj = Blocked_List(user_id=twitr.login_id,
                                            share='no')
                temp_list = list()
            for id_ in getids:
                if id_ not in temp_list:
                    temp_list.append(int(id_))
            user_obj.blocked_users = temp_list
            user_obj.save()
        data = dict()
        blocked_ids = list()
        getids = twitr.get_blocked_ids()
        try:
            blockedListObj = Blocked_List.objects.get(user_id=twitr.login_id)
            temp_list = eval(blockedListObj.blocked_users)
            for id_ in getids:
                if id_ not in temp_list:
                    temp_list.append(int(id_))
            blockedListObj.blocked_users = temp_list
        except:
            for id_ in getids:
                blocked_ids.append(int(id_))
            blockedListObj = Blocked_List(user_id=twitr.login_id,
                                            share='no',
                                            blocked_users=blocked_ids)
        blockedListObj.save()
        getids = twitr.get_followers()
        followers = list()
        for id_ in getids:
            followers.append((id_.get('id'),
                              id_.get('name'),
                              id_.get('screen_name'))
                            )
        data = {'followers': followers,'user':twitr.login_name, 'share': blockedListObj.share}
        return render_to_response("home.html",
                                  data,
                                  context_instance=RequestContext(request))
    return HttpResponseRedirect(reverse('index'))


def blocked_users(request):
    if "access_token" in request.session:
        twitr = Twit(request)
        blockListObj = Blocked_List.objects.get(user_id=twitr.login_id)
        blockedUsersList =  eval(blockListObj.blocked_users)
        if request.method == "POST":
            getids = request.POST.getlist('blocked_users')
            for id_ in getids:
                response = twitr.unblock_user(id_)
                blockedUsersList.remove(int(id_))
            blockListObj.blocked_users = blockedUsersList
            blockListObj.save()
        data = dict()
        blocked_users = list()
        getids = twitr.get_blocked_users()
        for id_ in getids:
            blocked_users.append((id_.get('id'),
                              id_.get('name'),
                              id_.get('screen_name'))
                            )
        data = {'blocked_users': blocked_users,'user':twitr.login_name, 'share': blockListObj.share}
        return render_to_response("blocked_users.html", data,
                                      context_instance=RequestContext(request))
    return HttpResponseRedirect(reverse('index'))


def blocked_lists(request):
    if "access_token" in request.session:
        twitr = Twit(request)
        if request.method == "POST":
            getids = request.POST.getlist('blocked_users')
            user_id = int(request.POST.getlist('user_list')[0])
            try:
                user_obj = Blocked_List.objects.get(user_id=twitr.login_id)
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
                        response = twitr.unblock_user(id_)
                        if id_ in temp_list:
                            temp_list.remove(int(id_))
                else:
                    subscribed_users.append(user_id)
                    for id_ in getids:
                        response = twitr.block_user(id_)
                        if not int(id_) in temp_list:
                            temp_list.append(int(id_))
                user_obj.blocked_users = temp_list
                user_obj.subscribed_users = subscribed_users
            except:
                for id_ in getids:
                    response = twitr.block_user(id_)
                    temp_list.append(int(id_))
                user_obj = Blocked_List(user_id=twitr.login_id,
                                        share='no',
                                        blocked_users=temp_list,
                                        subscribed_users=[user_id])
            user_obj.save()
        data = dict()
        blocked_data = dict()
        followers_ids = list()
        loggedUserBlockObj = Blocked_List.objects.get(user_id=twitr.login_id)
        followersList = twitr.get_followers()
        for follower in followersList:
            followers_ids.append(follower['id'])
            try:
                user_obj = Blocked_List.objects.get(user_id=int(follower['id']))
                if (user_obj.share == 'public') and (eval(user_obj.blocked_users) != []):
                    follower_blocks = list()
                    try:
                        if int(user_obj.user_id) in eval(loggedUserBlockObj.subscribed_users):
                            alredy_subscribed = True
                        else:
                            alredy_subscribed = False
                    except:
                        alredy_subscribed = False
                    for blocked_id in eval(user_obj.blocked_users):
                        blocked_user = twitr.show_user(blocked_id)
                        follower_blocks.append((blocked_id, blocked_user.get('name'),blocked_user.get('screen_name')))
                    blocked_data[(follower['id'],follower['name'],follower['screen_name'],str(alredy_subscribed))]=follower_blocks
            except:
                pass
        friendsList = twitr.get_friends()
        import pdb
        pdb.set_trace()
        
        for friend in friendsList:
            if not friend['id'] in followers_ids:
                try:
                    user_obj = Blocked_List.objects.get(user_id=int(friend['id']))
                    if (user_obj.share == 'private') and (eval(user_obj.blocked_users) != []):
                        #append to data
                        friend_blocks = list()
                        try:
                            if int(user_obj.user_id) in eval(loggedUserBlockObj.subscribed_users):
                                alredy_subscribed = True
                            else:
                                alredy_subscribed = False
                        except:
                            alredy_subscribed = False
                        for blocked_id in eval(user_obj.blocked_users):
                            blocked_user = twitr.show_user(blocked_id)
                            friend_blocks.append((blocked_id,
                                                 blocked_user.get('name'),
                                                 blocked_user.get('screen_name')))
                        blocked_data[(friend['id'],friend['name'],
                              friend['screen_name'],str(alredy_subscribed))] = friend_blocks
                except:
                    pass
        data = {'blocked_data': blocked_data,'user':twitr.login_name, 'share':loggedUserBlockObj.share}
        return render_to_response("blocked_lists.html", data,
                                  context_instance=RequestContext(request))
    return HttpResponseRedirect(reverse('index'))


def change_share(request):
    twitr = Twit(request)
    if "access_token" in request.session:
        shareStatus = request.GET['shareStatus'];
        loggedUserBlockObj = Blocked_List.objects.get(user_id=twitr.login_id)
        loggedUserBlockObj.share = shareStatus
        loggedUserBlockObj.save()
        HttpResponseRedirect(reverse('home'))
    return HttpResponseRedirect(reverse('index'))