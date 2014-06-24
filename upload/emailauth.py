'''
Created on Sep 6, 2012

@author: vedara
'''
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.validators import email_re

class EmailAuthenticator(ModelBackend):
    def authenticate(self, username=None, password=None,**kwargs):
        #If username is an email address, then try to pull it up
        user=None
        if email_re.search(username):
            try:
                user = User.objects.get(email=username)
              
            except User.DoesNotExist:
                return None
        '''
        else:
            #We have a non-email address username we
            #should try username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        '''   
        if user.check_password(password):
            return user
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        