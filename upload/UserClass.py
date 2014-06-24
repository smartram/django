'''
Created on Sep 6, 2012

@author: vedara
'''

from django.shortcuts import get_object_or_404
from models import person,RelationShip
from django.core.cache import cache
from django.contrib.auth.models import User
from stringroot.settings import SITE_MEDIA

class UserDetails(object):
    userobj=None
    personobj=None
    
    def __init__(self,personobj=None):
        
        if personobj is not None:
            self.homedir=personobj.homedir
            self.username=personobj.username
            self.image=SITE_MEDIA + personobj.image.name
            self.aboutme=personobj.aboutme
            self.personobj=personobj
            self.school=personobj.school
        else:
            self.userobj=None
            self.personobj=None
            self.username=" "
            self.image=" "
            self.homedir=" "
            self.list_friends={}
            self.email=" "
            self.quota=-1
            self.city=""
            self.country=""
            self.aboutme=""
            self.school=""
            
              
    def getUserInfo(self,userobj):
        personobj= get_object_or_404(person, pid=userobj)
        #person.objects.get(pid=userobj)
        #self.userobj=userobj
        self.personobj=personobj
        self.homedir=personobj.homedir
        self.username=userobj.username
        self.image=SITE_MEDIA + personobj.image.name
        self.aboutme=personobj.aboutme
        self.school=personobj.school
    
def getUserDetails(userobj):
    userd=UserDetails()
    userd.getUserInfo(userobj) #populates itself
    return userd
