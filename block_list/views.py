# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
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
    if not "access_token" in request.session:
        return HttpResponseRedirect(reverse('index'))
    twitr = Twit(request)
    #POST method lets you block the selected users
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
                temp_list.append(id_)
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
                temp_list.append(id_)
        blockedListObj.blocked_users = temp_list
    except:
        for id_ in getids:
            blocked_ids.append(id_)
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
    data = {'followers': followers,'user':twitr.login_name}
    return render_to_response("home.html",
                              data,
                              context_instance=RequestContext(request))


def blocked_users(request):
    if not "access_token" in request.session:
        return HttpResponseRedirect(reverse('index'))
    twitr = Twit(request)
    if request.method == "POST":
        getids = request.POST.getlist('blocked_users')
        for id_ in getids:
            response = twitr.unblock_user(id_)
    data = dict()
    blocked_users = list()
    getids = twitr.get_blocked_users()
    for id_ in getids:
        blocked_users.append((id_.get('id'),
                          id_.get('name'),
                          id_.get('screen_name'))
                        )
    data = {'blocked_users': blocked_users,'user':twitr.login_name}
    return render_to_response("blocked_users.html", data,
                                  context_instance=RequestContext(request))


def blocked_lists(request):
    if not "access_token" in request.session:
        return HttpResponseRedirect(reverse('index'))
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
    getids = twitr.get_friends_ids()
    #check the ids in db for loop
    for id_ in getids:
        try:
            user_obj = Blocked_List.objects.get(user_id=int(id_))
            friend = twitr.show_user(id_)
            if (user_obj.share == 'no') and (eval(user_obj.blocked_users) != []):
                #append to data
                friend_blocks = list()
                try:
                    loggedUserBlockObj = Blocked_List.objects.get(user_id=int(twitr.login_id))
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
                blocked_data[(friend.get('id'),friend.get('name'),
                      friend.get('screen_name'),str(alredy_subscribed))] = friend_blocks
        except:
            pass
    data = {'blocked_data': blocked_data,'user':twitr.login_name}
    return render_to_response("blocked_lists.html", data,
                              context_instance=RequestContext(request))