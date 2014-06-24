'''
Created on Feb 8, 2013

@author: venkataedara
'''
from upload.models import RelationShip
from upload.UserClass import SITE_MEDIA
from upload.friends import getfriends

MAX_FANS=10

class Fans(object):
    def __init__(self):
        self.username=""
        self.image=""
        self.aboutme=""
        self.is_friend=False


def getallfans(personobj):
    #fanskey=personobj.username + ".fans"
    #fans_list=cache.get(fanskey)
    
    fans=RelationShip.objects.filter(to_friend=personobj)[0:MAX_FANS]
    fans_list=[f.from_friend for f in fans]
    
    return fans_list
        
def populatefans(personobj):
    fans= personobj.to_friend_set.all()[0:MAX_FANS]
    fans_list=[f.from_friend for f in fans]
    return fans_list

def getfansbyindex(personobj,startindex):
    fans=personobj.to_friend_set.all()[startindex:startindex+MAX_FANS]
    fans_list=[f.from_friend for f in fans]
    return fans_list

def getfanscount(personobj):
    count=RelationShip.objects.filter(to_friend=personobj).count()
    return count

def getfans(personobj,currentuser=False):
    allfans=populatefans(personobj)
    allfriends=None
    if currentuser:
        allfriends=getfriends(personobj) 
    fans_list=[]
    count=0
    for f in allfans:
        ud=Fans()
        ud.image=SITE_MEDIA + f.image.name
        ud.username=f.username
        ud.aboutme=f.aboutme
            
        if allfriends is not None and f.username in allfriends:
            ud.is_friend=True
        fans_list.append(ud)
        count=count+1
        
    return count,fans_list
    
def getnextfans(personobj,startindex,currentuser=False):
    nextfans=getfansbyindex(personobj,startindex)
    allfriends=None
    if currentuser:
        allfriends=getfriends(personobj) #allfriends is a dictionary
    fans_list=[]
    count=0
    for f in nextfans:
        ud=Fans()
        ud.image=SITE_MEDIA + f.image.name
        ud.username=f.username
        ud.aboutme=f.aboutme
        if allfriends is not None and f.username in allfriends:
            ud.is_friend=True
        fans_list.append(ud)
        count=count+1
        
    return count,fans_list
    