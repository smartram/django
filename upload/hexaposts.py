'''
Created on Nov 3, 2012

@author: vedara
'''
from django.core.cache import cache
from upload.models import Posts,SharedPosts,get_filetype
from upload.UserClass import *
from upload.fans import getallfans
from upload.includes import log,photodim
from upload.initposts import *
from upload.friends import getfriends_forposts
import datetime,os
from django.utils import timezone
from upload.postdate import gettimeformat
factor=10

class UserPosts:
    def __init__(self):
        self.username=""
        self.image=""
        self.code=""
        self.text=""
        self.is_shared=False
        self.iamowner=False
        self.sharedbyme=False
        self.shared_by=[]
        self.postid=0
        self.timestamp=""
        self.timeformat=""
        self.ftype=""# icon for attachment type
        self.sharingusers=""
        self.posttype=""
        self.width=None
        self.height=None
        self.albumcover=""
        

class UserMemory(UserPosts):
    def __init__(self):
        UserPosts.__init__(self)
        self.day=1
        self.year=2013
        self.month=8

def get_firstposts(personobj,num_of_posts=MAX_POSTS): # get individual posts
    my_posts=init_posts(personobj,num_of_posts)
    return my_posts
    
def get_invposts(request,personobj):
    #total_count=get_postscount(username)
    
    myposts=get_firstposts(personobj)
    i=0
        
    image=SITE_MEDIA + personobj.image.name   
    inv_posts=[]
    now=timezone.now()
    for post in myposts:
        user_post=UserPosts()
        user_post.username=post.ownerid.username
        user_post.text=post.text
        user_post.code=post.code # for file attatchments
        user_post.posttype=post.filetype
        user_post.albumcover=post.albumcover
        if post.filetype in get_filetype:
            #if image is there, get url of image itself.
            if user_post.posttype==7 or user_post.posttype==8 or user_post.posttype==9:
                user_post.ftype=SITE_MEDIA + personobj.homedir + "/" + post.filename
            elif user_post.posttype == 10:
                user_post.ftype=os.path.join(SITE_MEDIA,personobj.homedir,post.filename,post.albumcover)
            else:
                user_post.ftype=get_filetype[post.filetype]
                
            if post.width and post.height:
                user_post.width,user_post.height=photodim(post.width,post.height)
            
        user_post.image=image
        timestamp=post.timestamp
        user_post.timeformat=gettimeformat(now,timestamp)

        if request.user.username == personobj.username:
            user_post.iamowner=True
        user_post.postid=post.postid
        inv_posts.append(user_post)
        i=i+1
    

    if i > 0:
        request.session['last_index']=i
        request.session['latest_index']=inv_posts[0].postid
    else:
        request.session['last_index']=0
    

    return inv_posts    

def getnext_invposts(request,username):
    from friends import checkfriend
    if not username:
        return[]
    personobj=None
    showProfile=False
    #getprofile=True
    if (username == request.user.username): # check whether we r viewin our own profile
        if 'userprofile' in request.session:
            personobj=request.session['userprofile'].personobj
            #getprofile=False
            showProfile=True
    
    else:
        personobj=person.objects.get(username=username)
        if personobj.profiletype == 1:
            showProfile=True
        elif personobj.profiletype == 2:# user opted for only friends should view profile
            showProfile=checkfriend(username,request.user.username)
        else:
            showProfile=False
        
    if not showProfile:
        return []    
    
    lastindex=int(request.session['last_index'])
    nextposts=get_nextposts(personobj,lastindex)
    len_posts=0
    inv_posts=[]
    now=timezone.now()

    for post in nextposts:
        user_post=UserPosts()
        len_posts=len_posts + 1
        user_post.username=post.ownerid.username
        user_post.text=post.text
        user_post.code=post.code # for file attatchments
        user_post.posttype=post.filetype
        user_post.albumcover=post.albumcover
        if post.filetype in get_filetype:
            #if image is there, get url of image itself.
            if user_post.posttype==7 or user_post.posttype==8 or user_post.posttype==9:
                user_post.ftype=SITE_MEDIA + personobj.homedir + "/" + post.filename
            elif user_post.posttype == 10:
                user_post.ftype=os.path.join(SITE_MEDIA,personobj.homedir,post.filename,post.albumcover)
            else:
                user_post.ftype=get_filetype[post.filetype]
        
            if post.width and post.height:
                user_post.width,user_post.height=photodim(post.width,post.height)
                 
            
        user_post.image=SITE_MEDIA + personobj.image.name
        user_post.postid=post.postid
        if request.user.username == personobj.username:
            user_post.iamowner=True

        timestamp=post.timestamp
        user_post.timeformat=gettimeformat(now,timestamp)

        inv_posts.append(user_post)
    
    if len_posts > 0:
        request.session['last_index']=lastindex + len_posts  
       
    return inv_posts
    
   
def get_firstwallposts(request,list_personobj):

    count=len(list_personobj)
    if count==0:
        return []
    normalposts=init_wallposts(list_personobj)
    sharedposts=init_sharedposts(list_personobj)
    allposts=mergeposts(normalposts,sharedposts)
    return allposts

def fetch_wallposts(list_personobj,startindex,endindex):
    
    count=len(list_personobj)
    if count==0:
        return []
    normalposts=list(Posts.objects.filter(ownerid__in=list_personobj).filter(mark_delete=False).order_by("-timestamp")[startindex:endindex])
    sharedposts=list(SharedPosts.objects.filter(user__in=list_personobj).order_by("-timestamp")[startindex:endindex/3])
    allposts=mergeposts(normalposts,sharedposts)
    return allposts
    
def get_wallposts(request):
    # get friends from cache for username and call get_firstwallposts
    wallkey=request.user.username + ".wallposts"
    if 'userprofile' in request.session:
        personobj=request.session['userprofile'].personobj
    else:
        personobj=person.objects.get(pid=request.user)
    allposts=cache.get(wallkey)
    if allposts is not None and len(allposts) > 0:
        wallposts=allposts[0:MAX_POSTS]
        return wallposts
     
    if 'userprofile' in request.session:
        ownerprofile=request.session['userprofile']
    else:
        ownerprofile=getUserDetails(request.user)
    
    list_friends=getfriends_forposts(ownerprofile.personobj)    
    list_friends.append(ownerprofile.personobj)
    allposts=get_firstwallposts(request,list_friends)
    
    count=0
    wall_posts=[]
    for post in allposts:
        if post.username == request.user.username:
            post.iamowner=True
        if str(request.user.username) in post.shared_by:
            post.sharedbyme=True
        
        if(count<MAX_POSTS):
            wall_posts.append(post)
            
        count=count+1
        
    if count > 0:
        cache.set(wallkey,allposts)
                    
        return wall_posts
    else:
        return []
        
def getnext_wallposts(request):
    if request.user.is_authenticated():
        pindex=0
        wallkey=request.user.username + ".wallposts"
        allposts=cache.get(wallkey)
                
        if 'last_index' in request.session:
            pindex=request.session['last_index']
           
        if 'userprofile' in request.session:
            personobj=request.session['userprofile'].personobj
        else:
            personobj=person.objects.get(pid=request.user)
      
                
        if allposts is not None:
            countall=len(allposts)
            wallposts=allposts[pindex:pindex+MAX_POSTS]
            count=len(wallposts)
            if count > 0:
                request.session['last_index']=pindex+count
                return wallposts
            else: # if cache doesn't have that many of posts. get from db and add it to cache.
                list_friends=getfriends_forposts(personobj)
                list_friends.append(personobj) # just add own profile also to get list of own  posts
    
                startindex=pindex
                endindex=pindex + MAX_POSTS
                wallposts=fetch_wallposts(list_friends,startindex,endindex)
                for post in wallposts:
                    if str(request.user.username) in post.shared_by:
                        post.sharedbyme=True
                    if request.user.username == post.username:
                        post.iamowner=True
        
                count=len(wallposts)
                '''
                if countall < 30:#dont add all posts to cache. only 30 allowed in cache.
                    allposts.extend(wallposts)
                    cache.set(wallkey,allposts)
                '''
                request.session['last_index']=pindex+count
                return wallposts
                
        # if cache expires      
        list_friends=getfriends_forposts(personobj)
        list_friends.append(personobj)
        startindex=0
        endindex=pindex+MAX_POSTS
        allposts=fetch_wallposts(list_friends,startindex,endindex) # get posts from 0 to pindex+MAX_POSTS becoz cache expired.
        count=len(allposts)
        if count > 0:
            for post in allposts:
                if str(request.user.username) in post.shared_by:
                    post.sharedbyme=True
                if request.user.username == post.username:
                    post.iamowner=True
            cache.set(wallkey,allposts)
            request.session['last_index']=count
            return allposts[pindex:endindex]
        else:
            return []
    
def get_latestwallposts(request):
    from friends import getfriends_forposts
    personobj=None
    wallkey=request.user.username + ".wallposts"
    if 'userprofile' in request.session:
        personobj=request.session['userprofile'].personobj
    else:
        personobj=person.objects.get(username=request.user.username)     
   
    if 'latest_timestamp' in request.session:
        latest_tstamp=request.session['latest_timestamp']
        startindex=0
        endindex=MAX_POSTS
        list_friends=getfriends_forposts(personobj)
        normalposts=fetch_normalposts_timestamp(list_friends,latest_tstamp,startindex,endindex)
        
        list_friends.append(personobj)
        sharedposts=fetch_sharedposts_timestamp(list_friends,latest_tstamp,startindex,endindex)
        
        #add current user also to dictionary and pass it to mergeposts. becoz there will be own sharedposts
        latest_wallposts=mergeposts(normalposts,sharedposts)
        count=len(latest_wallposts)
        allposts=cache.get(wallkey)
        pos=0
        
        if 'last_index' in request.session:
            last_index=request.session['last_index']
        else:
            last_index=0
            
        if count > 0:
            request.session['last_index']=count + last_index
            request.session['latest_timestamp']=latest_wallposts[0].timestamp
            
            if allposts is not None:
                for post in latest_wallposts:
                    if str(request.user.username) in post.shared_by:
                        post.sharedbyme=True
                        
                    allposts.insert(pos,post)
                    #pos=pos+1
            
                cache.set(wallkey,allposts)
            
            return latest_wallposts
        
        else:
            return []     
    else:
        # some thing fishy happened if latest_timestamp is not there
        list_friends=getfriends_forposts(personobj)
        allposts=get_firstwallposts(request,list_friends)
        
        for post in allposts:
            if str(request.user.username) in post.shared_by:
                post.sharedbyme=True

        count=len(allposts)
        if count > 0:
            request.session['last_index']=count
            request.session['latest_timestamp']=allposts[0].timestamp
            cache.set(wallkey,allposts)
        return allposts
                       
def mergeposts(normalposts,sharedposts):
    total_sposts=len(sharedposts)
    total_uposts=len(normalposts)
    wall_posts=[]
    now=timezone.now()
    if total_sposts==0 and total_uposts==0:
        return []
    
    elif total_sposts==0:
        
        for post in normalposts:
            user_post=UserPosts()
            user_post.username=post.ownerid.username
            user_post.text=post.text
            user_post.code=post.code # for file attachments
            user_post.posttype=post.filetype
            user_post.albumcover=post.albumcover
            if user_post.posttype and user_post.posttype in get_filetype: 
                if user_post.posttype==7 or user_post.posttype==8 or user_post.posttype==9:
                    user_post.ftype=SITE_MEDIA + post.ownerid.homedir + "/" + post.filename
                elif user_post.posttype == 10:
                    user_post.ftype=os.path.join(SITE_MEDIA,post.ownerid.homedir,post.filename,post.albumcover)
                else:
                    user_post.ftype=get_filetype[post.filetype]
        
                if post.width and post.height:
                    user_post.width,user_post.height=photodim(post.width,post.height)
               
                
            user_post.postid=post.postid
            timestamp=post.timestamp
            user_post.timeformat=gettimeformat(now,timestamp)
            user_post.timestamp=timestamp 
            user_post.image=SITE_MEDIA + post.ownerid.image.name
            wall_posts.append(user_post)
        
        return wall_posts    
             
    elif total_uposts==0:
        dict_posts={} # used to find same posts shared by users
        for post in sharedposts:
            user_post=UserPosts()
            user_post.postid=post.postid.postid
            if user_post.postid not in dict_posts:
                dict_posts[user_post.postid]=[post.user.username]
            else:
                list_sharedusers=dict_posts[user_post.postid]
                list_sharedusers.append(post.user.username)
                dict_posts[user_post.postid]=list_sharedusers
                
            user_post.shared_by=dict_posts[user_post.postid]
            user_post.is_shared=True
            user_post.username=post.postid.ownerid.username
            user_post.text=post.postid.text
            user_post.code=post.postid.code # for file attachments
            user_post.posttype=post.postid.filetype
            user_post.albumcover=post.postid.albumcover
            if user_post.posttype and user_post.posttype in get_filetype:
                if user_post.posttype==7 or user_post.posttype==8 or user_post.posttype==9:
                    user_post.ftype=SITE_MEDIA + post.postid.ownerid.homedir + "/" + post.postid.filename
                elif user_post.posttype == 10:
                    user_post.ftype=os.path.join(SITE_MEDIA,post.postid.ownerid.homedir,post.postid.filename,post.postid.albumcover)
                else:
                    user_post.ftype=get_filetype[user_post.posttype]
                    
                if post.postid.width and post.postid.height:
                    user_post.width,user_post.height=photodim(post.postid.width,post.postid.height)
                                  
            timestamp=post.timestamp
            user_post.timestamp=timestamp

            user_post.timeformat=gettimeformat(now,timestamp)

            user_post.image=SITE_MEDIA + post.postid.ownerid.image.name
            wall_posts.append(user_post)
        return wall_posts
            
    else:
        normal_uposts=[]
        shared_uposts=[]
        dict_posts={}
        for spost in sharedposts:
            user_post=UserPosts()
            user_post.postid=spost.postid.postid
            
            if user_post.postid not in dict_posts:
                dict_posts[user_post.postid]=[spost.user.username]
            else:
                list_sharedusers=dict_posts[user_post.postid]
                list_sharedusers.append(spost.user.username)
                dict_posts[user_post.postid]=list_sharedusers
                
            user_post.shared_by= dict_posts[user_post.postid]
            user_post.is_shared=True
            user_post.username=spost.postid.ownerid.username
            user_post.text=spost.postid.text
            user_post.code=spost.postid.code
            user_post.posttype=spost.postid.filetype
            user_post.albumcover=spost.postid.albumcover
            if user_post.posttype and user_post.posttype in get_filetype:
                if user_post.posttype==7 or user_post.posttype==8 or user_post.posttype==9:
                    user_post.ftype=SITE_MEDIA + spost.postid.ownerid.homedir + "/" + spost.postid.filename
                elif user_post.posttype == 10:
                    user_post.ftype=os.path.join(SITE_MEDIA,spost.postid.ownerid.homedir,spost.postid.filename,spost.postid.albumcover)
                else:
                    user_post.ftype=get_filetype[user_post.posttype]
              
                    #user_post.width=spost.postid.width
                    #user_post.height=spost.postid.height
                if spost.postid.width and spost.postid.height:
                    user_post.width,user_post.height=photodim(spost.postid.width,spost.postid.height)
            
          
            timestamp=spost.timestamp
            user_post.timeformat=gettimeformat(now,timestamp)
            user_post.timestamp=spost.timestamp
            user_post.image=SITE_MEDIA + spost.postid.ownerid.image.name
            shared_uposts.append(user_post)
            
        dict_posts={} # free memory
        for npost in normalposts:
            user_post=UserPosts()
            user_post.username=npost.ownerid.username
            user_post.text=npost.text
            user_post.code=npost.code
            user_post.posttype=npost.filetype
            user_post.albumcover=npost.albumcover
            if user_post.posttype and user_post.posttype in get_filetype:
                if user_post.posttype==7 or user_post.posttype==8 or user_post.posttype==9:
                    user_post.ftype=SITE_MEDIA + npost.ownerid.homedir + "/" + npost.filename
                elif user_post.posttype == 10:
                    user_post.ftype=os.path.join(SITE_MEDIA , npost.ownerid.homedir, npost.filename,npost.albumcover)
                else:
                    user_post.ftype=get_filetype[npost.filetype]
               
                        
                if npost.width and npost.height:
                        user_post.width,user_post.height=photodim(npost.width,npost.height)
                    
                
            user_post.postid=npost.postid
            timestamp=npost.timestamp
            user_post.timeformat=gettimeformat(now,timestamp)

            user_post.timestamp=npost.timestamp
            user_post.image=SITE_MEDIA + npost.ownerid.image.name
            normal_uposts.append(user_post)
        normalposts=[]
        sharedposts=[] # free up the memory.    
      
        # merging code comes now. assuming timestamps are in descending order
        if normal_uposts[0].timestamp < shared_uposts[0].timestamp:
            pos=0
            for post in shared_uposts:#insert at head of list,as sharedposts are latest ones
                normal_uposts.insert(pos,post)
                pos=pos+1
            
        else:# iterate through shared posts and insert them in normal posts
            it1=iter(normal_uposts)
            val1=it1.next() #iterator for normal posts
            pos=0
            for val2 in shared_uposts:
                while val1.timestamp > val2.timestamp:
                    try:
                        pos=pos+1
                        val1=it1.next()
                    except StopIteration:#iterator it1 throws exception when it reached end.so catch it and break from loop.
                        break
                normal_uposts.insert(pos,val2)
                pos=pos+1
    
        wall_posts=normal_uposts
        
        return wall_posts  