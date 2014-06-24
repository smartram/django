'''
Created on Apr 24, 2013

@author: venkataedara
'''
from upload.stdincludes import *

@login_required
def invite_friends(request):
    from django.core.validators import email_re
    if(request.user.is_authenticated()):
        if 'userprofile' in request.session:
            profile=request.session['userprofile']
        else:
            profile=getUserDetails(request.user)
            request.session['userprofile']=profile
            
        if 'emails' in request.POST : 
            #validate the emails.
            email_list=request.POST["emails"] # returns email ids 
            if(str(email_list).find(";")==-1 and str(email_list).count("@") > 1):
                return HttpResponse("<p> wrong format , please seperate addresses by ; </p>")
            
            emails=email_list.split(";")
            allemails=[x for x in emails if  email_re.search(x)]
            if len(allemails)==0:
                message="<p> Enter Proper Emails </p>"
                return HttpResponse(message)
                        
            subject="%s%s"%("join me in stringroot.com by ",request.user.username)

            message=render_to_string('registration/inviteuser_emailformat.html',{'image':profile.image,'username':request.user.username})

            #check whether user already sent invitations or not. if not then only insert into db
            #user + invemail is primary key . 
            try:
                invall=list(UserInvite.objects.select_related('emailid').filter(from_friend=request.user , emailid__in=allemails))
                invitedemails=[x.emailid for x in invall]
                allemails=[x for x in allemails if x not in invitedemails]
            except UserInvite.DoesNotExist:
                pass
           
            if len(allemails)==0:
                message="<p> You have already sent Invitations </p>"
                return HttpResponse(message)
            
            user_inv=[UserInvite(from_friend=request.user,emailid=str(mailid)) for mailid in allemails]
            UserInvite.objects.bulk_create(user_inv)
            t = threading.Thread(target=send_emails,args=(allemails,subject,message))
            t.setDaemon(True)
            t.start()
            #send_emails(emails,subject,message)
            message="<p style='font-size:16px;color:blue'> User Invitations sent </p>"
            return HttpResponse(message)
           
        else:
            variables=RequestContext(request,{'banner':False,'image':profile.image,'username':profile.username,'currentuser':True})
            return render_to_response('invite_friends.html',variables)
        

def accept_friend(request,username):
    try:
        fromuser=person.objects.get(username=username)
        request.session['fromuser']=fromuser
        return redirect('/register')
    except person.DoesNotExist:
        raise Http404
        
        
def friendsuknow(request):
    from random import randint
    personobj=None
    if 'userprofile' in request.session:
        personobj=request.session['userprofile'].personobj
    
    #initially get CEO, VC profile    
    list_suggestions=[]
    Rfriend=namedtuple('Rfriend', 'username image')
    response_data={}
    pall=person.objects.filter(country=personobj.country).filter(pid__is_active=True).exclude(username=personobj.username).values("username","image").order_by("-pid")[0:10]
    if len(pall) == 0:
        pall=person.objects.all().exclude(username=personobj.username).values("username","image").order_by("-pid")[0:10]

        
    list_suggestions=[Rfriend(x['username'], SITE_MEDIA +  x['image']) for x in pall]
    html=render_to_string('friendsuknow.html',{'users':list_suggestions})    
    response_data['html']=html        
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
    
    '''
    if personobj is not None:
        dict_friends=getfriends(personobj)
        totalfriends=len(dict_friends)
        if totalfriends > 0:
            f_index=randint(0,totalfriends-1)
            count=0
            friendobj=None
            
            anyusername=dict_friends.keys()[f_index]
            
            friendobj=dict_friends[anyusername]
            other_friends=getfriends(friendobj)#get friends of ur friend
            if personobj.username in other_friends:
                del other_friends[personobj.username] # remove original user from friends list, otherwise user will see his own profile in list
                        
            if len(other_friends) > 0:
                pall=[other_friends[x] for x in other_friends if x not in dict_friends]
                list_suggestions=[Rfriend(x.username, SITE_MEDIA +  x.image.name) for x in pall]
            else: # my friend doesnt have any friends.
                pall=person.objects.filter(country=personobj.country).exclude(username=personobj.username).values("username","image").order_by("pid")[0:10]
                list_suggestions=[Rfriend(x['username'], SITE_MEDIA +  x['image']) for x in pall]
        else: # user does not have friends at all
            pall=person.objects.filter(country=personobj.country).exclude(username=personobj.username).values("username","image").order_by("pid")[0:10]
            list_suggestions=[Rfriend(x['username'], SITE_MEDIA +  x['image']) for x in pall]

    else: #something fishy happened. user is not authenticated.
        pall=person.objects.values("username","image").order_by("pid")[0:8]
        list_suggestions=[Rfriend(x['username'], SITE_MEDIA +  x['image']) for x in pall]
        
    html=render_to_string('friendsuknow.html',{'users':list_suggestions})    
    response_data['html']=html        
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")  
    '''


def getffcount(request,username):
    from upload.fans import getfanscount

    if str(username) == str(request.user.username):
        currentuser=True
        userprofile=request.session['userprofile']
        personobj=userprofile.personobj
        
    else:
        userobj = get_object_or_404(User, username=username) #whose page this is 
        currentuser=False
        userprofile=getUserDetails(userobj)
        personobj=userprofile.personobj
   
    ckey1=username + ".friendscount"
    ckey2=username + ".fanscount"
        
    friendscount=cache.get(ckey1)
    fanscount=cache.get(ckey2)
    
    if friendscount is None:
        friendscount=getfriendscount(personobj)
     
    if fanscount is None:
        fanscount=getfanscount(personobj) 
        cache.set(ckey2,fanscount)
    response_data={}
    
    response_data['friendscount']=friendscount
    response_data['fanscount']=fanscount
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")    
  
  
def view_friends(request,username):
    currentuser=False
        
    if str(request.user.username) == str(username):
        #viewing own friends
        currentuser=True
        if 'userprofile' in request.session:
            personobj=request.session['userprofile'].personobj
        else:
            personobj=get_object_or_404(person,pid=request.user)
     
    else:  
        personobj = get_object_or_404(person, username=username)
        
    list_friends=showfriends(personobj)
    request.session['findex']=len(list_friends)
    userimage=SITE_MEDIA + personobj.image.name    
    variables=RequestContext(request,{'username':username,
                                      #'user':user,
                                      'currentuser':currentuser,
                                      'friends':list_friends,
                                       'image':userimage,
                                       'aboutme':personobj.aboutme,
                                       'show_friends':True})
    return render_to_response('viewing_friends.html',variables)
 
def view_nextfriends(request,username):
    currentuser=False
    personobj=None
    status=-1
    html="Error Occurred, try later"
    if 'findex' in request.session:
        findex=request.session['findex']
    else:
        findex=0
     
        
    if str(request.user.username) == str(username):
        #viewing own friends
        currentuser=True
        if 'userprofile' in request.session:
            personobj=request.session['userprofile'].personobj
        else:
            personobj=get_object_or_404(person,pid=request.user)
     
    else: 
        personobj = get_object_or_404(person, username=username)
      
    list_friends=showfriends(personobj,findex)
    count_friends=len(list_friends)
    if count_friends > 0:
        status=0
    findex=findex + count_friends
    request.session['findex']=findex
    variables=RequestContext(request,{'friends':list_friends,
                                      'currentuser':currentuser
                                      })
    
    html=render_to_string('view_nextfriends.html',variables)
    response_data={}
    response_data['html']=html
    response_data['status']=status
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")    

    
     
def view_fans(request,username):
    from upload.fans import getfans,getfanscount
    currentuser=False
    show_fans=False
    if str(request.user.username) == str(username):
        #viewing own fans
        currentuser=True
        if 'userprofile' in request.session:
            personobj=request.session['userprofile'].personobj
        else:
            personobj=get_object_or_404(person,pid=request.user)
    else: 
        personobj = get_object_or_404(person, username=username)
        
    count,list_fans=getfans(personobj,currentuser)
    
    fanscount=getfanscount(personobj)
    friendscount=getfriendscount(personobj)
    
    if count > 0:
        show_fans=True
        request.session['fans_index']=count
 
    userimage=SITE_MEDIA + personobj.image.name    
    variables=RequestContext(request,{'username':username,
                                  #'user':user,
                                  'currentuser':currentuser,
                                  'fans':list_fans,
                                  'fanscount':fanscount,
                                   'friendscount':friendscount,
                                   'image':userimage,
                                   'aboutme':personobj.aboutme,
                                   'show_fans':show_fans})

    return render_to_response('fanspage.html',variables)
 
     
def view_nextfans(request,username):
    from upload.fans import getnextfans
    currentuser=False
    status=-1
    html="Error Occurred, pls try again"
    
    #how many fans user already viewed
    if 'fans_index' in request.session:
        index=request.session['fans_index']
    else:
        index=0
        
    if request.user.username == username:
        currentuser=True
        personobj=request.session['userprofile'].personobj
        
    else:
        personobj = get_object_or_404(person, username=username)
        
    count,fans_list=getnextfans(personobj,index,currentuser)
    if count > 0:
        request.session['fans_index']=count+ index
        status=0
        
    html=render_to_string('nextfanspage.html', {
                                                'currentuser':currentuser,
                                                'fans':fans_list
                                                })
    response_data={}
    response_data['html']=html
    response_data['status']=status
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")    

def add_friend(request,username):
    if(request.user.is_authenticated()):
        #userobj = get_object_or_404(User, username=username)
        isadded=addfriend(request,username)
        if(isadded):
            ckey=request.user.username + ".friendscount"
            num_friends=cache.get(ckey)
            if num_friends is not None:
                num_friends=num_friends + 1
                cache.set(ckey,num_friends)
                
            return HttpResponse("<p class='notification'> Added as Friend </p>")
        else:
            return HttpResponse("<p class='notification'> Already following </p>")
        
    else:
        return HttpResponse("<p> Login is required to do this. <a href='/login'>login</a>")

def delete_friend(request,username):
    if(request.user.is_authenticated()):
        #friend_obj=get_object_or_404(User, username=username)
        is_deleted=deletefriend(request,username)
        
        if(is_deleted):
            return HttpResponse("<p> Deleted </p")
        else:
            return HttpResponse("<p>Error Occurred </p>")
    else:
        return HttpResponse("<p> Login is required to do this. <a href='/login'>login</a>")
