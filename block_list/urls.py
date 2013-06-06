from django.conf.urls import patterns, include, url

urlpatterns = patterns('block_list.views',
    url(r'^$', 'index', name='index'),
    url(r'^home/$', 'home', name='home'),
    url(r'^blocked_users', 'blocked_users', name='blocked_users'),
    url(r'^blocked_lists', 'blocked_lists', name='blocked_lists'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^change-share', 'change_share', name='change_share'),
)
