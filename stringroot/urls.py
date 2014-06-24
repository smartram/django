from django.conf.urls import patterns, include, url
from django.conf import settings
from upload.views import *
from upload.userviews import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

site_media ="/Users/venkataedara/workspace/stringroot/stringroot/site_media"
icons="/Users/venkataedara/workspace/stringroot/stringroot/site_media/icons"
css="/Users/venkataedara/workspace/stringroot/stringroot/site_media/css"

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hexashare.views.home', name='home'),
    # url(r'^hexashare/', include('hexashare.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    #url(r'^$',demo_page),
    url(r'^hexapost/$', upload_file),
    url(r'^memories/$', memories),
    url(r'^getmemories/$',getmemories),
    url(r'^getnextposts/$', get_nextuserposts),
    url(r'^postid/([\[\]A-Za-z_.0-9:,\-\(\)]+)$', postid),
    url(r'^$', main_page),
    url(r'^docomment/$',commentpost),
    url(r'^reportspam/$',markspam),
    url(r'^getnextwallposts/$',get_nextwposts),
    url(r'^getlatestwallposts/$',get_latestwposts),
    url(r'^sharepost/([0-9]+)/$',sharepost),
    url(r'^getrelatedposts/([\[\]A-Za-z_.0-9:,\-\(\)]+)$',getrelatedposts),
    url(r'^deletepost/([0-9]+)/$',deletepost),
    url(r'^user/([A-Za-z_.0-9]+)/$', user_page),
    url(r'^sendmessage/([A-Za-z_.0-9]+)$', sendmessage),
    url(r'^viewchat/([A-Za-z_.0-9]+)$', view_chat),
    url(r'^getlatestchat$', getlatestchat),#pending view
    url(r'^sendchat/$',send_chat),
    url(r'^inbox/$',inbox),
    url(r'^delall/([A-Za-z_.0-9]+)$',delallmsgs),
    url(r'^invite/$',invite_friends),
    #url(r'^send_invitations/$',send_invitations),
    url(r'^friend_accept/([A-Za-z_.0-9]+)/$',accept_friend),
    url(r'^friend_add/([A-Za-z_.0-9]+)/$',add_friend),
    url(r'^friend_delete/([A-Za-z_.0-9]+)/$',delete_friend),
    url(r'^friendsumayknow/$',friendsuknow),
    url(r'^list_friends/([A-Za-z_.0-9]+)/$', view_friends),
    url(r'^getnextfriends/([A-Za-z_.0-9]+)/$', view_nextfriends),
    url(r'^view_fans/([A-Za-z_.0-9]+)/$', view_fans),
    url(r'^getcount/([A-Za-z_.0-9]+)/$',getffcount),
    url(r'^getnextfans/([A-Za-z_.0-9]+)/$', view_nextfans),
    url(r'^register/$',registeruser),
    url(r'^login/$', login_page),
    url(r'^logout/$',logout_page),
    url(r'^confirm/(\w+)/$',confirm_user),
    url(r'^reset/$',reset_password),
    url(r'^editprofile/$',edit_profile),
    url(r'^changepassword/$',changepassword),
    url(r'^search/$',search),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
     { 'document_root': site_media }),
    url(r'^icons/(?P<path>.*)$', 'django.views.static.serve',
     { 'document_root': icons }),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
     { 'document_root': css })
  
  
                       
)
