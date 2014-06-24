# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from stringroot.settings import STATIC_URL,STATIC_ROOT,MEDIA_ROOT
# Create your models here.

import socket


DEL_MSGS_FROMUSER=1
DEL_MSGS_TOUSER=2
DEL_ALL=3

#default_ipaddr=socket.gethostbyname(socket.gethostname())

#give unique code each extension
allowed_filetypes={ 'pdf':1,
           'ppt':2,
           'pptx':2,
           'docx':3,
           'doc':3,
           'flv':4,
           'avi':5,
           'mp4':5,
           #'mpeg':5,
           'mp3':6,
           'jpeg':7,
           'jpg':7,
           'png':8,
           'gif':9 ,
           'folderalbum':10  }


get_filetype={1:'/icons/pdf.png',
              2:'/icons/ppt-icon.jpg',
              3:'/icons/doc.png',
              4:'/icons/videoreel.png',
              5:'/icons/videoreel.png',
              6:'/icons/mp3icon.JPG',
              7:'/icons/photo.png',
              8:'/icons/photo.png',
              9:'/icons/photo.png',
              10:'/icons/photo.png'
              }

#profile_type has to be 2powern fashion. 
profile_type={1:'public',
              2:'friends',
              4:'onlyme',
              8:'deactivate'
              }

class person(models.Model):
        country=models.CharField(max_length=30,default=None,null=True)
        city=models.CharField(max_length=30,default=None,null=True)
        homedir=models.CharField(max_length=300,null=True)
        username=models.CharField(max_length=30,primary_key=True)
        quota=models.IntegerField(default=None)
        email=models.EmailField()
        machine=models.TextField(default=socket.gethostname())
        image=models.ImageField("Profile Pic",upload_to="thumbs",blank=True,null=True)
        aboutme=models.TextField(max_length=160,default=None,null=True)
        pid=models.ForeignKey(User)
        profiletype=models.IntegerField(default=1) # 1 is public,2 for friends,4 only private.
        school=models.CharField(default=None,max_length=72,null=True)
        
class UserActivation(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

        
class Posts(models.Model):
    postid=models.AutoField(primary_key=True)
    timestamp=models.DateTimeField(default=timezone.now())
    text=models.CharField(max_length=4096,null=True,blank=True)
    filename=models.CharField(max_length=100,null=True)
    filetype=models.IntegerField(null=True)
    filesize=models.IntegerField(default=0)
    code=models.CharField(max_length=32)# create index on code.
    mark_delete=models.BooleanField(default=False) # have a celery task which deletes these posts
    ownerid=models.ForeignKey(person,related_name='powner_id')
    width=models.IntegerField(null=True)
    height=models.IntegerField(null=True)
    albumcover=models.CharField(max_length=100,null=True)

class Memories(models.Model):# purely personal 
    id=models.AutoField(primary_key=True)
    memtext=models.CharField(max_length=4096,null=True)    
    filename=models.CharField(max_length=100,null=True)
    filetype=models.IntegerField(null=True)
    #filesize=models.IntegerField(default=0)
    code=models.CharField(max_length=32)# create index on code.
    mark_delete=models.BooleanField(default=False) # have a celery task which deletes these posts
    ownerid=models.ForeignKey(person,related_name='mowner_id')
    width=models.IntegerField(null=True) # for photo
    height=models.IntegerField(null=True)# for photo
    timestamp=models.DateTimeField(default=timezone.now())
    month=models.IntegerField(null=False) # for memory
    day=models.IntegerField(null=False)# for memory
    year=models.IntegerField(null=False) # for memory
    albumcover=models.CharField(max_length=100,null=True)
      
class SharedPosts(models.Model):
    postid=models.ForeignKey(Posts,related_name='postid_id')
    user=models.ForeignKey(person,related_name='sharedby_id')
    timestamp=models.DateTimeField(default=timezone.now())
    memid=models.ForeignKey(Memories,null=True,related_name='memid_id')
    
class RelationShip(models.Model):
    from_friend=models.ForeignKey(person,related_name='friend_set')
    to_friend=models.ForeignKey(person,related_name='to_friend_set')    
    is_friend=models.BooleanField(default=True) # set it to False if user blocks other user.
    
    class Admin:
        pass
    class Meta:
        unique_together = (('to_friend', 'from_friend'), )

class UserInvite(models.Model):
    from_friend=models.ForeignKey(User,related_name='from_friend')
    emailid=models.EmailField(max_length=60,null=True)
    
    class Admin:
        pass
    class Meta:
        unique_together= (('from_friend','emailid'), )
    
class Comments(models.Model):
    commentid=models.AutoField(primary_key=True)
    postid=models.ForeignKey(Posts)
    user=models.ForeignKey(person)
    comment=models.CharField(max_length=90)
    is_spam=models.BooleanField(default=False)
  
'''
when user deletes the conversation
flag msgs as DEL_MSGS_FROMUSER for msgs from user to other user 
flag msgs as DEL_MSGS_TOUSER for msgs from other user to me. 
'''    
    
class Messages(models.Model):
    messageid=models.AutoField(primary_key=True)
    from_user=models.ForeignKey(person,related_name='fromuser')
    to_user=models.ForeignKey(person,related_name='touser')
    message=models.TextField(max_length=100)
    timestamp=models.DateTimeField(default=timezone.now())
    unread=models.BooleanField(default=True)
    delmode=models.PositiveIntegerField(default=0)

class Hits(models.Model):
    postcode=models.ForeignKey(Posts,related_name="post_code")
    hits=models.BigIntegerField(default=0)
 
'''    
all=Messages.objects.raw("UPDATE upload_messages set delmode=delmode|1 where from_user_id='rao_soft27' and to_user_id='sailaja.cln'")
''' 
    
   