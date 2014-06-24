'''
Created on Dec 7, 2012

@author: vedara
'''

from upload.models import Posts,SharedPosts,get_filetype
#from django.core.cache import cache
from django.db.models import Q
from collections import namedtuple
from upload.includes import levenshtein

FETCHED_POSTS=50
SHARED_POSTS=20
MAX_POSTS=15
MIN_POSTS=5


#this is for user page. only user owned posts
def init_posts(personobj,num_of_posts):
    allposts=Posts.objects.select_related().filter(ownerid=personobj).filter(mark_delete=False).order_by("-postid")[0:num_of_posts]
    return list(allposts)

def get_postscount(personobj):
    num_of_posts=Posts.objects.filter(ownerid=personobj).filter(mark_delete=False).order_by("-postid").count()
    return num_of_posts

def get_nextposts(personobj,last_index):
    next_index=last_index+ MAX_POSTS
    allposts=Posts.objects.select_related().filter(ownerid=personobj).filter(mark_delete=False).order_by("-postid")[last_index:next_index]
    return list(allposts)


# this is for wall. 
def init_wallposts(persons_list):
    allposts=Posts.objects.select_related('ownerid__username','ownerid__image','ownerid__homedir','ownerid__profiletype').filter(ownerid__in=persons_list).filter(mark_delete=False).order_by("-timestamp")[0:FETCHED_POSTS]
    return list(allposts)

def init_sharedposts(persons_list):
    sharedposts=SharedPosts.objects.select_related('postid','user__username','user__image','user__homedir','user__profiletype').filter(user__in=persons_list).filter(postid__mark_delete=False).order_by("-timestamp")[0:SHARED_POSTS]
    list_shared=list(sharedposts)
    return list_shared

def fetch_normalposts_timestamp(persons_list,latest_timestamp,startindex,endindex):
    count=len(persons_list)
    if count==0:
        return []
    nposts=list(Posts.objects.select_related('ownerid__username','ownerid__image','ownerid__homedir','ownerid__profiletype').filter(ownerid__in=persons_list).filter(mark_delete=False).filter(timestamp__gt=latest_timestamp).order_by("timestamp")[startindex:endindex])
    return nposts

def fetch_sharedposts_timestamp(persons_list,latest_timestamp,startindex,endindex):
    count=len(persons_list)
    if count==0:
        return[]
    sposts=list(SharedPosts.objects.select_related('user__username','user__image','user__homedir','user__profiletype').filter(user__in=persons_list).filter(timestamp__gt=latest_timestamp).order_by("timestamp")[startindex:endindex/3])
    return sposts   


def fetch_relatedposts(rfilename,rfiletype,username,code):
     
    count=len(rfilename)
    if count > 3:
        #list_words=[filename[0:x] for x in xrange(count,3,-1)]
        list_words= rfilename.split()
        if len(list_words) == 0:
            list_words=[rfilename[x:count-x] for x in xrange(1,count/2)]
        rlist =Posts.objects.filter(mark_delete=False).filter(reduce(lambda x, y: x | y, [Q(filename__contains=word) for word in list_words]) | Q(filetype=rfiletype))
        related_list=[x for x in rlist]
        
        #sort the list according filenames close to parametre filename
        related_list=sorted(related_list,key=lambda x:levenshtein(rfilename,x.filename))
        Rpost=namedtuple('Rpost', 'filename ftype code') # namedtuple faster than Class objects in python
        
        list_posts=[Rpost(x.filename,get_filetype[x.filetype],x.code) for x in related_list if x.code != code]
        #del related_list
        return set(list_posts)
    else:
        return []    
 
def  spaceleft(personobj):
    from django.db.models import Sum
    quota=personobj.quota
    quotainMB= quota 
    space_occupied=Posts.objects.filter(ownerid=personobj).filter(mark_delete=False).aggregate(Sum('filesize'))
    spacesum=space_occupied['filesize__sum']
    if spacesum is not None:
        space_occupied=(spacesum/1048576) # get in MB
        remspace = quotainMB - space_occupied
    else:#user did not upload anything.
        remspace=quotainMB

    return remspace