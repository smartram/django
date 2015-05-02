'''
Created on Mar 23, 2013

@author: venkataedara
'''
from UserClass import *
            
MAX_F_COUNT=10

def getfriendscount(personobj):
    ckey=personobj.username + ".friendscount"
    count=cache.get(ckey)
    if count is None:
        count=RelationShip.objects.filter(from_friend=personobj).count()
        cache.set(ckey,count)
        return count
    else:
        return count
        
def getfriends(personobj):
    fkey=personobj.username + ".friends"
    dict_friends=cache.get(fkey)
    if dict_friends is None:
        dict_friends=populatefriends(personobj)
        cache.set(fkey,dict_friends)    
    return dict_friends

def getfriends_forposts(personobj): # call this method for getting list of friends for wall
    dict_friends=getfriends(personobj)
    list_friends=[dict_friends[x] for x in dict_friends.keys() if dict_friends[x].profiletype==1]
    
    other_friends=[dict_friends[x] for x in dict_friends.keys() if dict_friends[x].profiletype==2]
    mutual_friends=amifriend(other_friends,personobj)
    list_friends.extend(mutual_friends)
    return list_friends
    

def getallfriendids(personobj):
    fkey=personobj.username + ".friends"
    dict_friends=cache.get(fkey)
    if dict_friends is None:
        dict_friends=populatefriends(personobj)
    list_fids=[dict_friends[f].id for f in dict_friends ] # dict_friends[f] is person row.
    return list_fids

        

def getfriends_aslist(personobj):
    username=personobj.username
    fkey=username + ".friends"
    dict_friends=cache.get(fkey)
    if dict_friends is None:
        dict_friends=populatefriends(personobj)
        cache.set(fkey,dict_friends)
    friends=[UserDetails(dict_friends[x]) for x in dict_friends.keys()]
    
    return friends
    
   
def populatefriends(personobj):
    allfriends=personobj.friend_set.all() #returns person tuples
    allfriends=[f.to_friend for f in allfriends if f.is_friend==True]
    dict_friends={}
    for f in allfriends:
        dict_friends[f.username]=f
    del  allfriends # release memory 
    return dict_friends 

def addfriend(request,tousername):
    fkey=request.user.username + ".friends"
    try:
        topersonobj=person.objects.get(username=tousername)
    except person.DoesNotExist:
        return False
    dict_friends=cache.get(fkey)
    if 'userprofile' in request.session:
        frompersonobj=request.session['userprofile'].personobj
    else:
        fromuser=getUserDetails(request.user)
        frompersonobj=fromuser.personobj
            
    if dict_friends is not None:#cache not empty
        
        if tousername in dict_friends:
            return False # already a friend. something error happened
        
        else: #we have person object of user, so add it to cache.    
            #friendship,create = RelationShip.objects.get_or_create(from_friend=frompersonobj, to_friend=topersonobj)
            dict_friends[tousername]=topersonobj
            cache.set(fkey,dict_friends)
    try:
        friendship,create = RelationShip.objects.get_or_create(from_friend=frompersonobj, to_friend=topersonobj)
        if create:
            setnumoffriends(frompersonobj)
            return True
    except Exception:
        pass
    return False

def showfriends(personobj,count=0):
    if personobj is None:
        return []
    friends_list=getfriends_aslist(personobj)[count:count+MAX_F_COUNT]
    return friends_list

def deletefriend(request,tousername):
    fkey=request.user.username + ".friends"
    ckey=request.user.username + ".friendscount"

    dict_friends=cache.get(fkey)
    
    try:
        topersonobj=person.objects.get(username=tousername)
    except person.DoesNotExist:
        return False
    
    if 'userprofile' in request.session:
        frompersonobj=request.session['userprofile'].personobj
    else:
        fromuser=getUserDetails(request.user)
        frompersonobj=fromuser.personobj
    
    
    if dict_friends is not None:# cache exists. remove from cache 
        if tousername in dict_friends:
            dict_friends[tousername]=""
            del dict_friends[tousername]
            cache.set(fkey,dict_friends)
            cache.set(ckey,len(dict_friends))        
        else:#not ur friend itself. friend not in cache
            return False
    try:
        f=RelationShip.objects.get(from_friend=frompersonobj,to_friend=topersonobj)
        f.delete()
        return True
    except Exception:
        pass
    
    return False
   
def checkfriend(username,tousername):
    fkey=username + ".friends"
    dict_friends=cache.get(fkey)
    
    try:
        topersonobj=person.objects.get(username=tousername)
    except person.DoesNotExist:
        return False
    
    
    if dict_friends is not None:
        if tousername in dict_friends: #O(1) search in hash_map of user name and friends
            return True
        else:
            return False
    else:#cache is empty..so check in db.
        try:
            frompersonobj=person.objects.get(username=username)
            f=RelationShip.objects.get(from_friend=frompersonobj,to_friend=topersonobj,is_friend=True)
            if f:
                return True
        except RelationShip.DoesNotExist:
            return False
    
def mutualfriends(username1,username2):
    dict1=getfriends(username1)
    dict2=populatefriends(username2)
    len1=len(dict1.keys())
    len2=len(dict2.keys())
    
    common_friends=[]
    #if dict1 has less elements then iterate through dict1 and search in dict2. otherwise vice versa
    if len1 < len2:
        for friend in dict1.keys():
            if friend in dict2:
                fri=UserDetails()
                fri.username=dict1[friend].pid.username # dict1[friend] is person object
                fri.image=SITE_MEDIA + dict1[friend].image.name
                fri.aboutme=dict1[friend].aboutme
                fri.country=dict1[friend].country
                fri.city=dict1[friend].city
                common_friends.append(fri)
                
    else:
        for friend in dict2.keys():
            if friend in dict1:
                fri=UserDetails()
                fri.username=dict1[friend].pid.username # dict1[friend] is person object
                fri.image=SITE_MEDIA + dict1[friend].image.name
                fri.aboutme=dict1[friend].aboutme
                fri.country=dict1[friend].country
                fri.city=dict1[friend].city
                common_friends.append(fri)
    
    return common_friends


def setnumoffriends(personobj):
    username=personobj.username
    ckey=username + ".friendscount"
    numoffriends=cache.get(ckey)
    if numoffriends is not None:
        cache.incr(ckey)
    else:
        fkey=username + ".friends"
        dict_friends=cache.get(fkey)
        if dict_friends is not None:
            cache.set(ckey,len(dict_friends.keys()))
        else:
            count=getfriendscount(personobj)
            cache.set(ckey,count)
      
def amifriend(list_persons,personobj):  #check whether personobj is friend of list_persons
    list_friends=RelationShip.objects.filter(from_friend__in=list_persons,to_friend=personobj).filter(is_friend=True)
    list_fri=[x.from_friend for x in list_friends]
    return list_fri

def searchfriends(personobj,username_tosearch):
    dict_friends=getfriends(personobj)
    list_users=[]
    for name in dict_friends.keys():
        if name.find(username_tosearch)==-1:
            continue
        else:
            list_users.append(dict_friends[name])
    return list_users
    

