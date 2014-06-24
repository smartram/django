# Create your views here.

from stdincludes import *


@login_required
def upload_file(request):
    
    youtubeurl=re.compile(r'(https?://)?(www\.)?youtube\.(com|nl)/watch\?(feature=player_detailpage&)?v=([-A-Za-z0-9_]+)')
    httpurl=re.compile(r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
    is_attachment=False
    profile=None   
    timestamp=timezone.now()

    if 'userprofile' in request.session:
        profile=request.session['userprofile']
        
    else:
        profile=getUserDetails(request.user) 
        request.session['userprofile']=profile
    
    if 'spaceleft' in request.session:
        spaceleft=int(request.session['spaceleft'])
    else:
        spaceleft=0    
        
    personobj=profile.personobj    
    response_data={}     
    status=0      
    dict_post={}
    filename=None
    filetype=None
    filesize=0
    width=None
    height=None
    albumcover=None
    
    if 'hexatext' in request.POST:
        hexamsg=str(request.POST['hexatext']).strip()
        match=youtubeurl.search(hexamsg)
        matchurl=httpurl.search(hexamsg)
        if match:
            youtube_param=match.group(5)
            
            embedcode="<embed width=\"400\" height=\"300\" src=\"http://www.youtube.com/v/%s\" type=\"application/x-shockwave-flash\">\
            </embed>"%(youtube_param)
            
            #embedcode="<object width=\"400\" height=\"300\"> <param name=\"movie\" value=\"http://www.youtube.com/v/%s\" /> <embed width=\"400\" height=\"300\" src=\"http://www.youtube.com/v/%s\" type=\"application/x-shockwave-flash\"/> </object> "%(youtube_param,youtube_param)
            
            
            hexamsg="%s%s" %(hexamsg,embedcode)# appending tats all.
        elif matchurl:
            url=matchurl.group()
            urltext="<a href='%s' target=\"_blank\">%s</a>"%(url,url)
            hexamsg=hexamsg.replace(url,urltext)
            
        
    if 'attachment' in request.FILES:
        if spaceleft <= 0:
            status=1
        else:
            #for key,fileobj in request.FILES.items():
            is_attachment=True
            list_fileobj=[afile for afile in request.FILES.getlist('attachment')]
            if len(list_fileobj) > 20:
                list_fileobj=list_fileobj[0:21]#allow only 20 files
            #list_fileobj=[y for x,y in request.FILES.items()]
            
            dict_post=handle_uploads(list_fileobj,hexamsg,personobj,profile.homedir)
            status=dict_post['status']
            if status == 0:
                filename=dict_post['filename']
                filetype=dict_post['filetype']
                filesize=dict_post['filesize']
                spaceleft=spaceleft-filesize
                request.session['spaceleft']=spaceleft
            
                if 'width' in dict_post:
                    width=dict_post['width']
                
                if 'height' in dict_post:
                    height=dict_post['height']
                    
                if 'albumcover' in dict_post:
                    albumcover=dict_post['albumcover']
                    
    random_code="%s%s"%(hexamsg,timestamp)
    #random_code=random_code.replace('[', '').replace('(','').replace(')','').replace(']','').replace(' ','').replace('+','').replace('\\','').replace('/','')
    random_code=removespecialchars(random_code)
    uniqcode="".join([choice(random_code + string.digits ) for x in range(1, 9)])
    

          
        
    if status==0:
        post=Posts.objects.create(timestamp=timestamp,ownerid=personobj,text=hexamsg,code=uniqcode,filename=filename,filetype=filetype,\
                                  width=width,height=height,albumcover=albumcover)
        #Hits.objects.create(postcode=post,hits=0) # needs to be celery job .

        #dict_post['post']=post
        #post=dict_post['post']
        username=profile.username
        user_post=UserPosts()
        user_post.username=username
        user_post.text=hexamsg
        user_post.image=profile.image
        user_post.postid=post.postid
        user_post.iamowner=True
        user_post.is_shared=False
        user_post.timeformat="now" #gettimeformat(now,post.timestamp)
        user_post.code=post.code
        user_post.timestamp=timestamp # will be used by main_page action to set latest timestamp for future wall posts
        user_post.posttype=post.filetype
        user_post.height=post.height
        user_post.width=post.width
        
        if is_attachment and post.filetype in get_filetype:
            if user_post.posttype==7 or user_post.posttype==8 or user_post.posttype==9:
                user_post.ftype=SITE_MEDIA + personobj.homedir + "/" + post.filename
            elif user_post.posttype == 10:
                
                user_post.ftype=os.path.join(SITE_MEDIA , personobj.homedir , post.filename , post.albumcover)
            else:
                user_post.ftype=get_filetype[post.filetype]
            
                
        if post.width and post.height:
            user_post.width,user_post.height=photodim(post.width,post.height)
           
            
        
        html= render_to_string('user_posts.html', {'image':profile.image,'username':profile.username,'text':hexamsg, 'id':post.postid, 'post':user_post})
        response_data['status']=0
        response_data['html']=html
        response_data['spaceleft']=spaceleft
        
        # update cache
        wallkey=username + ".wallposts"
        allposts=cache.get(wallkey)
        
        if allposts is not None:
            allposts.insert(0,user_post)
            cache.set(wallkey,allposts)
            index=0
        if 'last_index' in request.session:
            index=int(request.session['last_index']) + 1
            request.session['last_index']=index
        
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
    
    elif status==1:
        html=" <p style='color:red; font-size:16px'><b>  you exceeded your space limit. please delete posts with attachments  <a href='/user/%s'> here </a> </b> </p>"%(profile.username)
        response_data['status']=1
        response_data['html']=html
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
    else:
        html="<p style='color:red; font-size:16px'><b> Invalid file or error occurred  </b></p>" 
        #html=dict_post['html']
        response_data['status']=-1
        response_data['html']=html
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")    

     
def main_page(request):  
    from upload.fans import getfanscount
    if request.user.is_authenticated():
        
        allposts=get_wallposts(request)
        ckey1=request.user.username + ".friendscount"
        ckey2=request.user.username + ".fanscount"
        
        friendscount=cache.get(ckey1)
        fanscount=cache.get(ckey2)
        
        if 'userprofile' in request.session:
            userprofile=request.session['userprofile']  
            personobj=userprofile.personobj 
        if 'spaceleft' in request.session:
            quotaleft=request.session['spaceleft']
            
        if friendscount is None:
            friendscount=getfriendscount(userprofile.personobj)
        if fanscount is None:
            fanscount=getfanscount(userprofile.personobj)
            cache.set(ckey2,fanscount)
        count=len(allposts)    
        for post in allposts:
            if post.is_shared:
                list_users=post.shared_by
                html=render_to_string('sharedusers.html',{'list_users':list_users})
                post.sharingusers=html #convert to string again
            
        request.session['last_index']=count
    
        if count==0:
            allposts=[]           
            request.session['latest_timestamp']=timezone.now()
        else:

            request.session['latest_timestamp']=allposts[0].timestamp
     
        variables=RequestContext(request,{'username':request.user.username,
                                      'user':request.user,
                                      'country':personobj.country,
                                       'city':personobj.city,
                                       'image':userprofile.image,
                                       'aboutme':personobj.aboutme,
                                       'friendscount':friendscount,
                                       'fanscount':fanscount,
                                       'posts':allposts,
                                       'spaceleft':quotaleft
                                       })

        return render_to_response('main_page.html',variables)
    else:#if user is not authenticated display login form
        form = Login_Form()
        variables = RequestContext(request,{'form': form})
        return render_to_response('registration/login.html',variables)  

    
def login_page(request):
    
    form=Login_Form(request.POST)
     
    if form.is_valid():
        
        user=authenticate(username=form.clean_email(),password=form.clean_password())
        if user is not None:
            
            if user.is_active:
                form.has_errors=False
                #user.backend = 'django.contrib.auth.backends.ModelBackend'
               
                login(request,user)
                userprofile=getUserDetails(user)
                request.session['userprofile']=userprofile
                return redirect('/user/%s'%(user.username))
                
       
            else:
                form.has_errors=True 
                variables = RequestContext(request,{'form': form})
                return render_to_response('registration/login.html',variables)
       
                
        else:
            form.has_errors=True 
            variables = RequestContext(request,{'form': form})
            return render_to_response('registration/login.html',variables)
       
            
    form = Login_Form()
    #form.has_errors=True
    variables = RequestContext(request,{'form': form})
    return render_to_response('registration/login.html',variables)
        
def registeruser(request):
    from django.utils import timezone
    if request.method == 'POST':
        form=Registration(request.POST)
        if form.is_valid():
            try:
                password=form.clean_password2()
                
                email=form.clean_email()
                city=form.clean_city().lower()
                country_name=getcountry(form.clean_country())
                username=str(email).split('@')
                username=str(username[0]).lower()
                
                #allow create id like venkat.edara@gmail.com, venkat.edara@yahoo.com. 
                #emails are different, so allow users.
                try:
                    User.objects.get(username=username)
                    random_number=str(random.randint(2,100))

                    username=username + random_number
                except User.DoesNotExist:
                    pass
                salt = sha.new(str(random.random())).hexdigest()[:5]
                activation_key = sha.new(salt+email+"CEO Rams").hexdigest()
                #key_expires = datetime.datetime.today() + datetime.timedelta(2)
                key_expires = timezone.now() 
                
                user = User.objects.create_user(
                                        username=username,
                                        password=password,
                                        email=email                 
                                        )
                
                person1=person(pid=user,country=country_name,city=city,
                               quota=1,image="thumbs/stringroot.jpg",username=username)
                person1.save()
                
                # some user sent invitation to this member
                if 'fromuser' in request.session:
                    fromuser=request.session['fromuser']
                    
                    try:
                        user_inv=UserInvite.objects.get(from_friend=fromuser.pid,emailid=str(email))
                    except UserInvite.DoesNotExist:
                        user_inv=None
                       
                    
                    if user_inv is not None:
                        user.is_active=True
                        user.save()
                        user=authenticate(username=email,password=password)
                        friendship=RelationShip(from_friend=fromuser,to_friend=person1)
                        friendship.save()
                        friendship=RelationShip(from_friend=person1,to_friend=fromuser)
                        friendship.save()
                        #login user
                        login(request,user)
                        #create home dir for user for his stuff
                        random_number=str(random.randint(2,100))
                        homedir=os.path.join(MEDIA_ROOT , username) + random_number
                        homedirname=username + random_number
                        is_created=makedir(homedir)
                     
                        if is_created:
                            person.objects.filter(pid=user).update(homedir=homedirname)
                        #set session var
                        userprofile=getUserDetails(user)
                        request.session['userprofile']=userprofile                    
                               
                        return redirect('/user/%s'%(user.username))
        
                new_profile = UserActivation(user=user,
                              activation_key=activation_key,
                              key_expires=key_expires)    
                new_profile.save()
                user.is_active=False
                user.save()
                email_subject = 'Your new account for www.stringroot.com confirmation'
                email_body=render_to_string('registration/emailuser.html',{'username':email.split('@')[0],'code':activation_key})
                      
                email_user(email_subject,email_body,email)
        
                return render_to_response('registration/register_ack.html', {'created': True})
        
        
            except forms.ValidationError, error:
                errors=str(error).decode()
                form.has_errors=True
                variables = RequestContext(request,{'form': form, 'errors':errors})
                return render_to_response('registration/register.html',variables)
        else:
            
            form.has_errors=True
            variables = RequestContext(request,{'form': form})
            return render_to_response('registration/register.html',variables)
        
    else:
        errors=" "
        form=Registration()
        variables = RequestContext(request,{'form': form, 'errors':errors})
        return render_to_response('registration/register.html',variables)

def logout_page(request):
  
    if 'userprofile' in request.session:
        del request.session['userprofile']
    if 'last_index' in request.session:
        del request.session['last_index']
    #posts_key=str(request.user.username)+".wallposts"
    #friends_key=request.user.username + ".friends"
    #cache.delete_many([posts_key,friends_key])
    logout(request)
    
    #return render_to_response('registration/logged_out.html')
    return redirect('/')


def user_page(request, username):
    from upload.initposts import spaceleft
    request.session['visited']=username
    notfriend=True
    showProfile=False
    spaceleftinMB=0
    about=False
    
    userobj=request.user
    if str(username) == str(request.user.username): 
        currentuser=True
        showProfile=True
        userprofile=request.session['userprofile']
        personobj=userprofile.personobj
        spaceleftinMB=spaceleft(personobj)
        request.session['spaceleft']=spaceleftinMB
        about=True
        
    else:
        userobj = get_object_or_404(User, username=username) #whose page this is 
        currentuser=False
        userprofile=getUserDetails(userobj)
        personobj=userprofile.personobj
   
        if personobj.profiletype == 1:
            showProfile=True
        elif personobj.profiletype == 2:# user opted for only friends should view profile
            showProfile=checkfriend(username,request.user.username)
            
        else:
            showProfile=False
            
        if request.user.is_authenticated():
            if(checkfriend(request.user.username,username)):
                notfriend=False
   
    allposts=get_invposts(request,personobj)
     
             
    variables=RequestContext(request,{'username':username,
                                      'user':userobj,
                                      'currentuser':currentuser,
                                      'country':personobj.country,
                                       'city':personobj.city,
                                       'image':userprofile.image,
                                       'aboutme':personobj.aboutme,
                                       'notfriend':notfriend,
                                       'showprofile':showProfile,
                                       'posts':allposts,
                                       'about':about,
                                       'spaceleft':spaceleftinMB,
                                       'school': personobj.school
                                       })

    return render_to_response('user_page.html',variables)


  
def confirm_user(request,activation_key):
    from django.utils import timezone
    try:
        
        user_profile=UserActivation.objects.get(activation_key=activation_key)
        user_account = user_profile.user
        deltatime=timezone.now() - user_profile.key_expires  
        #if user_profile.key_expires < datetime.datetime.today():
        random_number= random.randint(2,100)   

        if deltatime.days > 2:
            user_account.delete()
            return render_to_response('registration/confirm.html', {'confirm': False})
            
        else:
            user_account.is_active = True
            user_account.save()

            homedir=os.path.join(MEDIA_ROOT , user_account.username) 
            homedir=homedir +  str(random_number)                     

            
            is_created=makedir(homedir)
            
            if is_created:
                member=person.objects.get(pid=user_account)
                member.homedir=user_account.username + str(random_number)
                member.save()
                
            user_profile.delete()
            variables=Context({'confirm':True})
            return render_to_response('registration/confirm.html', variables)
    except Exception:
        raise Http404
            
        
def reset_password(request):
    
    if request.method == 'POST':
        form=Password_Reset(request.POST)
        if form.is_valid():
        
            emailid=form.clean_email()
            password=generate_password()
            email_body="your password has been reset . please use %s for login "%(password)
            try:
                user=User.objects.get(email=emailid)
                user.set_password(password)
                user.save()
            except User.DoesNotExist:
                form=Password_Reset()
                variables = RequestContext(request,{'form':form,'title':"forgot password - stringroot", 'message':'Enter Valid Email'})
                return render_to_response('registration/forgot_password.html',variables)

                
            email_user("password reset for stringroot",email_body,emailid)
            variables=Context({'title':"forgot password - stringroot", 'message':'password is sent to your email id '})
            return render_to_response('registration/banner.html',variables)
        else:
            
            form=Password_Reset()
            variables = RequestContext(request,{'form':form,'title':"forgot password - stringroot", 'message':'Enter Email First '})
            return render_to_response('registration/forgot_password.html',variables)

        
    else:
        form=Password_Reset()
        variables=RequestContext(request,{'form':form,'confirm':'False'})
        return render_to_response('registration/forgot_password.html',variables)
        
@login_required
def edit_profile(request):    
    member=person.objects.select_related().get(pid=request.user)

    if 'userprofile' in request.session:
        user_obj=request.session['userprofile']
        
    if request.method == 'POST':
        form=EditProfile(request.POST,request.FILES)
           
        if form.is_valid():
            is_image=False
            country=form.get_country()
            city=form.get_city()
            aboutme=form.get_aboutme()
            visibility=int(form.get_visibility())
            school=form.get_school()
            firstname=form.get_firstname()
            lastname=form.get_lastname()
            save_name=False
            
            '''save first name and last name if it's not set in DB, otherwise ignore
            dont let user to change his names often'''
            if not member.pid.first_name:
                member.pid.first_name=firstname
                save_name=True
                
            if not member.pid.last_name:
                member.pid.last_name=lastname
                save_name=True
            
            if save_name:
                member.pid.save()
                  
            if len(country) > 0:
                member.country=country
                user_obj.country=country
            
            if len(city) > 0 :
                member.city=city
                user_obj.city=city
            
            if 'profilepic' in request.FILES: 
            
                member.image=request.FILES['profilepic']
                is_image=True
                
            if len(aboutme) > 0:
                member.aboutme=aboutme
                user_obj.personobj.aboutme=aboutme   
            
            if len(school) > 0:
                member.school=school
                user_obj.personobj.school=school
                
            member.profiletype=binarynum(visibility)
            member.save()
            
            if is_image:
                new_pic=os.path.join(MEDIA_ROOT + member.image.name)
                save_thumbnail(new_pic)
                
                user_obj.image="/site_media/" + member.image.name
            
            request.session['userprofile']=user_obj  
            #return redirect('/user/%s'%(request.user.username))
            resp="<p> changes are saved. <a href='/user/%s'>Click Here </a> </p>"%(request.user.username)
            return HttpResponse(resp)
        
        else: # if form is not valid
            #member=person.objects.get(pid=request.user)
            if 'school' in request.POST:
                member.school=request.POST['school']
                member.save()
                
            if 'profilepic' in request.FILES:
                member.image=request.FILES['profilepic']
                is_image=True
                if is_image:
                    member.save()
                    new_pic=os.path.join(MEDIA_ROOT + member.image.name)
                    save_thumbnail(new_pic)
                    user_obj.image="/site_media/" + member.image.name
             
            request.session['userprofile']=user_obj  
            resp="<p> changes are saved. <a href='/user/%s'>Click Here </a> </p>"%(request.user.username)
            return HttpResponse(resp)
    else: # if method id GET
        for c in countries:
            if member.country==c[1]:
                countrychoice=c[0]
                break
        visibility=member.profiletype;
        visibility_num=which_bitisset(visibility)
        form=EditProfile({'country':countrychoice,'city':member.city,'school':member.school,'aboutme':member.aboutme,
                          'firstname':member.pid.first_name,'lastname':member.pid.last_name,'visibility':visibility_num})
        form2=ChangePassword()
        variables=RequestContext(request,{'form':form,'form2':form2,'errors':False,'username':user_obj.username,'image':user_obj.image,
                                          'currentuser':True})
    
        return render_to_response('registration/editprofile.html',variables)
        
        
def get_nextuserposts(request):
    have_posts=False
    response_data={}
    if 'username' in request.GET:
        username=request.GET['username']
    list_posts=getnext_invposts(request,username)
    status=-1
    if len(list_posts) > 0:
        have_posts=True
        status=0
    
    html= render_to_string('invposts.html',{'have_posts':have_posts,'posts':list_posts})
    
    response_data['status']=status # 0 means successful
    response_data['html']=html
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def get_nextwposts(request):# for wall posts
    response_data={}

    if request.user.is_authenticated()==False:
        response_data['status']=-1 # 0 means successful
        response_data['html']="<p> not authenticated </p>"
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    have_posts=False
    list_posts=getnext_wallposts(request)
    for post in list_posts:
        if post.is_shared:
            list_users=post.shared_by
            html=render_to_string('sharedusers.html',{'list_users':list_users})
            post.sharingusers=html
            
    response_data={}
    status=-1
    if len(list_posts) > 0:
        have_posts=True
        status=0
        
    
    html= render_to_string('getposts.html',{'have_posts':have_posts,'posts':list_posts})
    response_data['status']=status
    response_data['html']=html
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def get_latestwposts(request): 
    have_posts=False
    response_data={}
    if request.user.is_authenticated()==False:
        response_data['status']=-1
        response_data['html']="<p> you are not authenticated </p>"
        return  HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
        
    list_posts=get_latestwallposts(request)
    count= len(list_posts)
    if count > 0:
        for post in list_posts:
            if post.is_shared:
                list_users=post.shared_by
                html=render_to_string('sharedusers.html',{'list_users':list_users})
                post.sharingusers=html
       
        have_posts=True
       
        html= render_to_string('getposts.html',{'have_posts':have_posts,'posts':list_posts})
        response_data['status']=0
        response_data['html']=html
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
    else:
        response_data={}
        html= render_to_string('getposts.html',{'have_posts':have_posts,'posts':list_posts})
        response_data['status']=1
        response_data['html']=html
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

@login_required
def sharepost(request,postid):
    response_data={}
    response_data['status']=1
    response_data['msg']="error occurred "
    uname=request.user.username
    save_to_db=True
    if 'userprofile' in request.session:
        personobj=request.session['userprofile'].personobj
    else:
        personobj=person.objects.get(username=request.user.username)
        
    try:
        post=Posts.objects.select_related('ownerid__username','ownerid__image','ownerid__profiletype','ownerid__homedir').filter(mark_delete=False).filter(postid=postid)[0]
        try:
            checkshared=SharedPosts.objects.filter(postid=post)
            sharedusers=[spost.user for spost in checkshared]
            for suser in sharedusers:
                if(str(suser.username)==str(request.user.username)):
                    response_data['msg']="you shared already"
                    save_to_db=False
                    break    
        except SharedPosts.DoesNotExist:
            save_to_db=True
        
    except Posts.DoesNotExist:
        response_data['msg']="cannot share the post now"
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
    
    #add to database if he didn't shared already
    timestamp=timezone.now()
    pkey=request.user.username + ".wallposts"
    allposts=cache.get(pkey)
    upost=UserPosts()
    upost.timestamp=timestamp;
    upost.timeformat="now"
    upost.is_shared=True
    upost.shared_by=[uname]
    upost.sharingusers="<a href='/user/%s'>%s</a>"%(uname,uname)
    upost.sharedbyme=True
    upost.text=post.text
    upost.username=post.ownerid.username
    upost.image=SITE_MEDIA + post.ownerid.image.name
    upost.code=post.code
    upost.postid=post.postid
    upost.posttype=post.filetype
    upost.albumcover=post.albumcover
    
    if post.filetype in get_filetype:
        if upost.posttype == 7 or  upost.posttype == 8 or  upost.posttype ==9:
            upost.ftype=SITE_MEDIA + post.ownerid.homedir + "/" + post.filename
        elif upost.posttype == 10:
            upost.ftype=os.path.join(SITE_MEDIA , post.ownerid.homedir  , post.filename,post.albumcover)
        else:
            upost.ftype=get_filetype[post.filetype]
        
            
        if post.width and post.height:
            upost.width,upost.height=photodim(post.width,post.height)

         
        
    if allposts is not None:
        
        allposts.insert(0,upost)
        
    if(save_to_db):
        spost=SharedPosts(postid=post,user=personobj,timestamp=timestamp)
        spost.save()
        request.session['latest_timestamp']=timestamp

        response_data['status']=0
        response_data['msg']="shared successfully "
        response_data['html']=render_to_string('getposts.html',{'posts':[upost],'have_posts':True })
            
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
 
@login_required 
def deletepost(request,postnum):
    response_data={}
    response_data['status']=1
    response_data['html']="error occurred "
    postid=int(postnum)
    if 'userprofile' in request.session:
        personobj=request.session['userprofile'].personobj
    else:
        personobj=person.objects.get(pid=request.user)
        
    if 'spaceleft' in request.session:
        spaceleft=request.session['spaceleft']
    else:
        spaceleft=spaceleft(personobj)    
    try:
        # a user can only delete his own posts
        #Posts.objects.filter(postid=postnum).filter(ownerid=personobj).update(mark_delete=True)
        post=Posts.objects.filter(postid=postnum).filter(ownerid=personobj)[0]
        filesizeinMB=post.filesize/1048576
        post.mark_delete=True
        post.save()
        
        spaceleft=spaceleft + filesizeinMB
        request.session['spaceleft']=spaceleft
        key=request.user.username + ".wallposts"
        wallposts=cache.get(key)
        if wallposts is not None:
            for post in wallposts:
                if post.postid==postid:
                    wallposts.remove(post)
                    break
            cache.set(key,wallposts)
        response_data['html']="post deleted"
        response_data['status']=0
        response_data['spaceleft']=spaceleft
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
    
    except Posts.DoesNotExist:
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
    
def postid(request,postidnum):
    from upload.tasks import save_hits_todb
    from os import listdir
    from os.path import isfile, join

    postcode=postidnum
    userobj=request.user
    ispdf=False
    isppt=False
    #isphoto=False
    isflash=False
    ismp3=False
    ismp4=False
    try:
        post=Posts.objects.select_related('ownerid__homedir','ownerid__username').filter(mark_delete=False).filter(code=postcode)[0]
        
        if post:
            from upload.comments import getcomments
            list_comments=getcomments(post)
            filetype=post.filetype
            filename=post.filename
            homedir=post.ownerid.homedir
            username=post.ownerid.username
            request.session['postid']=post.postid
            cache.set(postidnum,(filename,filetype,username))
            filelocation="%s%s%s%s" %(SITE_MEDIA, homedir,sep(),filename) #TO DO add ip address for users home dir multiple media servers
          
            #get the number of hits from cache or db.
            hitkey=postidnum +".hit"
            num_of_hits=cache.get(hitkey)
            if num_of_hits is None:
                try:
                    hitobj=Hits.objects.get(postcode__code=postcode)
                    num_of_hits=hitobj.hits
                except Hits.DoesNotExist:
                    hitobj=Hits.objects.create(postcode=post,hits=0) # needs to be celery job .
                    num_of_hits=0
                cache.set(hitkey,num_of_hits)
            
            cache.incr(hitkey)
            num_of_hits=num_of_hits+1
            save_hits_todb(postcode) # needs to be celery job
            
            if filetype==allowed_filetypes['pdf']:
                ispdf=True
                variables=RequestContext(request,{'user':userobj,'filelocation':filelocation,'uploaded_by':username,'comments':list_comments,'postcode':postcode,'hits':num_of_hits})    
                return render_to_response('pdf_attachments.html',variables)
              
                
            elif filetype==allowed_filetypes['ppt']:
                isppt=True
                    
            elif filetype==allowed_filetypes['flv']:
                isflash=True
            
            elif filetype==allowed_filetypes['mp4']:
                ismp4=True
                
            elif filetype==allowed_filetypes['mp3']:
                ismp3=True 
                variables=RequestContext(request,{'user':userobj,'filelocation':filelocation,
                                                  'uploaded_by':username,'comments':list_comments,'hits':num_of_hits,'postcode':postcode})    
                return render_to_response('music_attachment.html',variables)
              
                
                
            elif filetype==allowed_filetypes['jpeg'] or filetype==allowed_filetypes['jpg'] or filetype==allowed_filetypes['png'] or filetype==allowed_filetypes['gif']:
                #get remaining photos for slideshow
                 
                photos=Posts.objects.filter(ownerid__username=username).filter(mark_delete=False).filter(filetype__in=[7,8,9]).order_by('-timestamp')
                photo_locations=["%s%s%s%s"%(SITE_MEDIA,homedir,"/",x.filename) for x in photos if x.code != postcode]
                variables=RequestContext(request,{'user':userobj,'filelocation':filelocation,'uploaded_by':username,'comments':list_comments,
                                                  'photos':photo_locations,'hits':num_of_hits,'postcode':postcode})    
                return render_to_response('photo_attachments.html',variables)
            elif filetype == allowed_filetypes['folderalbum']:
                
                absdir=os.path.join(MEDIA_ROOT,homedir,post.filename)
                onlyfiles = [ f for f in listdir(absdir) if isfile(join(absdir,f)) ]
                firstphoto=onlyfiles[0]
                #why to calculate all photos dimensions which are almost same size.
                photoobj=getphotodesc(absdir,firstphoto)
                photo_objs=[Photo(i,photoobj.width,photoobj.height) for i in onlyfiles]
                
                for photo in photo_objs:#give web location now, add static parent path
                    photo.src=os.path.join(SITE_MEDIA,homedir,post.filename,photo.src)
             
                variables=RequestContext(request,{'user':userobj,'uploaded_by':username,'comments':list_comments,
                                                  'photos':photo_objs,'hits':num_of_hits,'postcode':postcode})

                return render_to_response('album_attachment.html',variables)

                        
            variables=RequestContext(request,{'user':userobj,'ispdf':ispdf,'isppt':isppt,'ismp3':ismp3,
                                              'isflv':isflash,'ismp4':ismp4,'filelocation':filelocation,
                                              'uploaded_by':username,'comments':list_comments,'postcode':postcode,
                                              'hits':num_of_hits})
            return render_to_response('attachment.html',variables)
                       
    except Posts.DoesNotExist:
        raise Http404    
   
    

@login_required
def commentpost(request):
    from upload.comments import postcomment
    
    response_data={}
    if 'commenttext' in request.POST and 'postid' in request.session:
        postid=request.session['postid']
        
        origpost=Posts.objects.get(postid=postid)
        text=str(request.POST['commenttext']).strip()
        personobj=request.session['userprofile'].personobj
        user_comment=postcomment(origpost,text,personobj)
        #variables=Context({'comment':user_comment})
        html= render_to_string('publishcomment.html',{'comment':user_comment},context_instance=RequestContext(request))
        response_data['status']=0
        response_data['html']=html
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
    else:
        response_data['status']=-1# error
        html="<p> Error Occurred. you cannot comment now.Try later </p>"
        response_data['html']=html
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")

@csrf_exempt 
def markspam(request):
    from upload.comments import markasspam
    if 'id' in request.POST:
        cid=request.POST['id']
        
        markasspam(cid) # use celery to update spam .enhancement
    response_data={}
    response_data['html']="<p> Reported as spam. comment will be deleted shortly </p>"
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
            
@login_required
def sendmessage(request,tousername):
       
    if 'userprofile' in request.session:
        frompersonobj=request.session['userprofile'].personobj
    else:
        userdetailsobj=getUserDetails(request.user)
        request.session['userprofile']=userdetailsobj
        frompersonobj=userdetailsobj.personobj
    
    try:
        topersonobj=person.objects.get(username=tousername)
        if 'Message' in request.POST:
            msgtext=request.POST['Message']
            msgtext=msgtext.strip()
            if len(msgtext) > 0:
                message=Messages()
                message.from_user=frompersonobj
                message.to_user=topersonobj
                message.message=msgtext
                message.timestamp=timezone.now()
                message.save()
                return HttpResponse("<p> Message Sent Successfully </p> ")
            return HttpResponse("<p> Error Occurred </p>")
        else:
            return HttpResponse("<p> Error Occurred </p>")
    except person.DoesNotExist:
        raise Http404

@login_required
def inbox(request):
    username=request.user.username
    if 'userprofile' in request.session:
        ownerobj=request.session['userprofile'].personobj
    else:
        ownerDetails=getUserDetails(request.user)
        request.session['userprofile']=ownerDetails.personobj
        ownerobj=ownerDetails.personobj
    image=SITE_MEDIA + ownerobj.image.name
    from upload.messages.showmessages import InitInboxMessages
    list_messages=InitInboxMessages(ownerobj)
    return render_to_response('inbox.html',{'messages':list_messages,'user':request.user,'image':image,'username':request.user.username})
   
def delallmsgs(request,username):
    from upload.messages.chatmessages import deletemessages
    response_data={}
    if request.user.is_authenticated():
        status=deletemessages(request.user.username,username) 
        if 'delfrom' in request.session:
            list_delusers=request.session['delfrom']
            list_delusers.extend([username])
            request.session['delfrom']=list_delusers
        else:
            request.session['delfrom']=[username]
        if(status):
            response_data['status']=0
            response_data['html']="error occurred"
            return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
        else:
            response_data['status']=-1
            response_data['html']="error occurred"
            return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")

    else:
        redirect('/login')       
                             
@login_required
def view_chat(request,username):
    total_unread=0
    tousername=username
    if 'userprofile' in request.session:
        ownerobj=request.session['userprofile'].personobj
    else:
        ownerDetails=getUserDetails(request.user)
        request.session['userprofile']=ownerDetails.personobj
        ownerobj=ownerDetails.personobj
    image=SITE_MEDIA + ownerobj.image.name
    from upload.messages.chatmessages import initChatMessages
    topersonobj=person.objects.get(username=tousername)
    image2=SITE_MEDIA + topersonobj.image.name
    chat_messages=initChatMessages(ownerobj,topersonobj)
    count_msgs=len(chat_messages)

    #calculate number of unread messages in this chat and inser into list, to mark them as read later.        
    #list comprehensions are 2x faster than list.append() method
    
    #list_unreadid=[msg.messageid for msg in chat_messages if msg.unread==True]
    #count_unread=len(list_unreadid)
    
    key=tousername + ".chatmsgid"
    if count_msgs > 0:
        request.session[key]=chat_messages[count_msgs-1].messageid #tail of list has latest msg id.
        
    variables=RequestContext(request,{'chatmessages':chat_messages,'user':request.user,
                                      'image':image,
                                      'username':request.user.username,
                                      'fromusername':tousername,
                                      'total_unread':total_unread,
                                      'fromuserimage':image2})

    return render_to_response('chat_page.html',variables)
    
    
@login_required
def send_chat(request):
    from upload.messages.chatmessages import create_chatmsg
    response_data={}
    response_data['status']=-1
    response_data['html']="<p> error occurred </p>"
    
    if 'username' in request.POST:
        username1=request.POST['username']
    if 'chattext' in request.POST:
        message=str(request.POST['chattext'])
        
    if 'userprofile' in request.session:
        ownerobj=request.session['userprofile'].personobj
    else:
        ownerDetails=getUserDetails(request.user)
        request.session['userprofile']=ownerDetails.personobj
        ownerobj=ownerDetails.personobj
    
    key=username1 +".personobj"
    topersonobj=cache.get(key)
    
    #if user is chatting online, put the topersonobj in cache to avoid too many queries
    if topersonobj is None:
        topersonobj=person.objects.get(username=username1)
        cache.set(key,topersonobj)
        
    if len(message.strip()) > 0:
        chatmsgs=create_chatmsg(ownerobj,topersonobj,message)
        response_data['html']=render_to_string('userchatmessage.html',{'username':request.user.username,'chatmessages':chatmsgs,'fromusername':username1},context_instance = RequestContext(request))
        response_data['status']=0
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
       
       
def getlatestchat(request):
    from upload.messages.chatmessages import getlatestchat,mark_ids_asread
    response_data={}
    response_data['status']=-1
    if 'userprofile' in request.session:
        ownerobj=request.session['userprofile'].personobj
    
    
    if 'username' in request.GET:
        fromusername=str(request.GET['username'])
        key="%s%s"%(fromusername,".chatmsgid") 
        latestchatid=0
        if key in request.session:
            latestchatid=request.session[key]
        
        personkey="%s%s"%(fromusername,".personobj") 
        frompersonobj=cache.get(personkey) #check cache whether personobj of other user is present or not
        if frompersonobj is None:
            try:
                frompersonobj=person.objects.get(username=fromusername)
                cache.set(personkey,frompersonobj)
            except person.DoesNotExist:
                return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
                
        #chatmessages is list of ChatMessages refer chatmessages.py
        chatmessages=getlatestchat(frompersonobj,ownerobj,latestchatid)
        total=len(chatmessages)
        if total > 0:
            
            list_ids=[msg.messageid for msg in chatmessages]
                            
            mark_ids_asread(list_ids)
            latestmsgid=chatmessages[0].messageid
            request.session[key]=latestmsgid
            response_data['html']=render_to_string('userchatmessage.html',{'username':request.user.username,'chatmessages':chatmessages,'fromusername':fromusername},context_instance = RequestContext(request))
            response_data['status']=0
            
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
        
            
def getrelatedposts(request,postidnum):
    filename=""
    filetype=-1
    username=""
    response_data={}
    
    post=cache.get(postidnum)
    if post is None:
        post=Posts.objects.select_related('ownerid__username').filter(mark_delete=False).filter(code=postidnum)[0]
        filename=post.filename
        filetype=post.filetype
        username=post.ownerid.username
    else:
        filename=post[0]
        filetype=post[1]
        username=post[2]
    
    list_posts=fetch_relatedposts(filename,filetype,username,postidnum)
    variables={'rposts':list_posts}
    html_code=render_to_string('relatedposts.html',variables)
    response_data['html']=html_code
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
    #return HttpResponse("<p> successfull </p>")

def search(request):
    #from friends import searchfriends
    MAX_COUNT=30
    isajax=False
    showmore=False
    startcount=0
    list_users=[]
    if 'userprofile' in request.session:
        personobj=request.session['userprofile'].personobj
    else:
        personobj=None
        
    if 'ajax' in request.GET:
        isajax=request.GET['ajax']
    
    if 'more' in request.GET:
        showmore=True
        
    if 'count' in request.GET:
        startcount=int(request.GET['count'])    
    if 'q' in request.GET:
        search_words=str(request.GET['q'])
        if len(search_words) >= 3:
            search_list=search_words.split()
            
            #search friends
            if personobj is not None:
                list_friends=searchfriends(personobj,search_words)
                if list_friends:
                    list_users=[UserDetails(x) for x in list_friends]
                
            if len(search_list) > 1:
                #add search by firstname, lastname also
                users=list(person.objects.filter(reduce(lambda x, y: x | y, [Q(username__contains=word) for word in search_list])).filter(profiletype=1) [0:MAX_COUNT])  
            else:
                users=list(person.objects.filter(username__contains=search_words).filter(profiletype=1) [startcount:startcount+MAX_COUNT])
            users=sorted(users,key=lambda x:levenshtein(search_words,x.username))
            users=[UserDetails(x) for x in users]
            users=set( users + list_users) # set will remove duplicates
            if isajax:
                return render_to_response('search_results.html',{'users_list':users,'showmore':showmore})
            else:
                count=len(users)
                if count < MAX_COUNT:
                    showmore=False
                return render_to_response('search.html',{'users_list':users,'user':request.user,'showmore':showmore})
        else:
            return HttpResponse("<p> <b> No Results </b> </p>")
    
    return HttpResponse("<p> <b> No Results </b> </p>")
    
def changepassword(request):
    response_data={}
    user=request.user

    if request.method == 'POST' and user.is_authenticated():
        form=ChangePassword(request.POST)
        if form.is_valid():
            try:
                current=form.get_currentpassword()
                validate=user.check_password(current)
                if not validate:
                    response_data['html']="<p  style='color:red;font-size:13px'> Password not correct </p>"
                    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
                newpassword=form.checkpassword()
                if newpassword:
                    user.set_password(newpassword)
                    user.save()
                    response_data['html']="<p  style='color:blue;font-size:13px'> Password Changed Successfully. please relogin <a href='/logout'>here </a>  </p>"
                else:
                    response_data['html']="<p style='color:red;font-size:13px'> <b> Passwords dont match. please enter same password twice </b> </p>"
                return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
             
            except Exception:
                response_data['html']="<p style='color:red;font-size:13px'> <b> Error Occurred. please fill all fields </b> </p>"
                return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
          
                 
        else:
            response_data['html']="<p style='color:red;font-size:13px'> <b> Error Occurred. please fill all fields </b> </p>"
            return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")

def memories(request):
    from memories import getMemoriesbyMonth, savememory
    if 'userprofile' in request.session:
        profile=request.session['userprofile']
        
    else:
        profile=getUserDetails(request.user) 
        request.session['userprofile']=profile
     
    personobj=profile.personobj
    if request.method == 'GET':
        response_data={}
        now=timezone.now()
        currmonth=now.month
        memories=getMemoriesbyMonth(personobj,currmonth)
        count=len(memories)
        request.session['mindex']=count
        memform=Memoryform({'month':currmonth,'day':now.day})
        variables=RequestContext(request,{'month':currmonth,
                                              'form':memform,'memories':memories,'show_button':True})
        return render_to_response('memories_2.html',variables)
    
    if request.method == 'POST':
        response_data={}
        filename=filetype=albumcover=None
        width=height=None
        hexamsg=None
        timestamp=timezone.now()
        youtubeurl=re.compile(r'(https?://)?(www\.)?youtube\.(com|nl)/watch\?(feature=player_detailpage&)?v=([-A-Za-z0-9_]+)')
        httpurl=re.compile(r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
        is_attachment=False
        status=0
        month=int(request.POST['month'])
        day=int(request.POST['day'])
        year=int(request.POST['year'])
        if 'hexatext' in request.POST:
            hexamsg=str(request.POST['hexatext']).strip()
            match=youtubeurl.search(hexamsg)
            matchurl=httpurl.search(hexamsg)
            if match:
                youtube_param=match.group(5)
            
                embedcode="<embed width=\"400\" height=\"300\" src=\"http://www.youtube.com/v/%s\" type=\"application/x-shockwave-flash\">\
            </embed>"%(youtube_param)
                hexamsg="%s%s" %(hexamsg,embedcode)# appending tats all.
        
            elif matchurl:
                url=matchurl.group()
                urltext="<a href='%s' target=\"_blank\">%s</a>"%(url,url)
                hexamsg=hexamsg.replace(url,urltext)
            
        
        if 'attachment' in request.FILES:
            #is_attachment=True
            list_fileobj=[afile for afile in request.FILES.getlist('attachment')]
            if len(list_fileobj) > 20:
                list_fileobj=list_fileobj[0:21]#allow only 20 files
            dict_post=handle_uploads(list_fileobj,hexamsg,personobj,profile.homedir)
            status=dict_post['status']
            if status == 0:
                filename=dict_post['filename']
                filetype=dict_post['filetype']
                filesize=dict_post['filesize']
                
                if 'width' in dict_post:
                    width=dict_post['width']
                if 'height' in dict_post:
                    height=dict_post['height']
                if 'albumcover' in dict_post:
                    albumcover=dict_post['albumcover']
    
        random_code="%s%s"%(hexamsg,timestamp)
        random_code=removespecialchars(random_code)
        uniqcode="".join([choice(random_code + string.digits ) for x in range(1, 9)])
        if status==0:
            memory=savememory({'timestamp':timestamp,'ownerid':personobj,'memtext':hexamsg,'code':uniqcode,
                        'filename':filename,'filetype':filetype,'width':width,'height':height,'albumcover':albumcover,
                        'month':month,'day':day,'year':year})
            
        html= render_to_string('monthmemories.html', {'memories':[memory],'show_button':False})
        response_data['status']=0
        response_data['html']=html
        
        if 'memory_index' in request.session:
            index=int(request.session['memory_index']) + 1
            request.session['memory_index']=index
        
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
    
    elif status==1:
        html=" <p style='color:red; font-size:16px'><b>  you exceeded your space limit. please delete posts or memories with attachments  </b> </p>"
        response_data['status']=1
        response_data['html']=html
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
    else:
        html="<p style='color:red; font-size:16px'><b> Invalid file or error occurred  </b></p>" 
        #html=dict_post['html']
        response_data['status']=-1
        response_data['html']=html
        return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")            

@login_required            
def getmemories(request):
    from memories import getMemoriesbyMonth

    show_button=True
    getmonth=False
    startindex=0
    
    if 'userprofile' in request.session:
        profile=request.session['userprofile']
        
    else:
        profile=getUserDetails(request.user) 
        request.session['userprofile']=profile
   
    personobj=profile.personobj
    getnext=False
    
    if 'month' in request.GET and request.GET['month'] > 0:
        getmonth=True
    if 'next' in request.GET and request.GET['next']== "true":#viewing next memories on scroll or showmore button
        getnext=True
        
    response_data={}
    currmonth=int(request.GET['month'])%13
    
    if getnext:
        show_button=False
        if 'mindex' in request.session:
            startindex=int(request.session['mindex'])
    
    if getmonth == False:
        return("/")
   
    memories=getMemoriesbyMonth(personobj,currmonth,startindex)
    count=len(memories)
    request.session['mindex']=count + startindex
    if count == 0:
        show_button=False
    
    html=render_to_string('monthmemories.html',{'month':currmonth,'show_button':show_button,
                                          'memories':memories})    
    response_data['html']=html
    response_data['status']=0
    return HttpResponse(simplejson.dumps(response_data),mimetype="application/json")
