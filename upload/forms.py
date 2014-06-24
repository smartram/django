'''
Created on Sep 6, 2012

@author: vedara
'''


from django import forms
from django.core.cache import cache
from django.core.validators import email_re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

countries=(
           (1,'India'),
           (2,'USA'),
           (3,'UK'),
           (4,'UAE'),
           (5,'Australia'),
           (6,'South Africa'),
           (7,'Newzealand'),
           (8,'Japan'),
           (9,'China'),
           (10,'Singapore'),
           (11,'Africa')
           
           )
visibility_choices=(
            (1,'public'),
            (2,'friends'),
            (3,'only me'),
            (4,'deactivate')
            )

months_choices=(
                (1,'Jan'),
                (2,'Feb'),
                (3,'Mar'),
                (4,'Apr'),
                (5,'May'),
                (6,'June'),
                (7,'July'),
                (8,'Aug'),
                (9,'Sep'),
                (10,'Oct'),
                (11,'Nov'),
                (12,'Dec')
                )

day_choices=((x,x) for x in xrange(31,0,-1))

def getyear():
    yearchoices=cache.get('yearchoices')
    if yearchoices is None:
        from django.utils import timezone
        curryear=timezone.now().year
        yearchoices=((x,x) for x in xrange(curryear,curryear-100,-1))
        cache.set('yearchoices',yearchoices)
    
    return yearchoices

def getcountry(index):
    c=dict(countries)
    return (c[index])
    
class Registration(forms.Form):
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput(),required=True)
    password2 = forms.CharField(label='Password (Again)',widget=forms.PasswordInput(),required=True)
    country=forms.ChoiceField(label="Country",choices=countries)
    city=forms.CharField(label="City")
    
    def clean_password2(self):
        
        if 'password1' in self.cleaned_data:
            password1=self.cleaned_data['password1']
            password2=self.cleaned_data['password2']
            if len(password1) <=2:
                raise forms.ValidationError('Passwords should be more than 3 characters.')
                
            if password1 == password2:
                return password2
            raise forms.ValidationError('Passwords do not match.')
    
    def clean_email(self):
        vals=self.clean()
        email=vals['email']
        if  email_re.search(email):
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                return email
            raise forms.ValidationError('email already registered')
        else:
            
            raise forms.ValidationError('invalid email id.')
    
    def clean_country(self):
        vals=self.clean()
        cindex=vals['country']
        return int(cindex)
 
    def clean_city(self):
        vals=self.clean()
        city=vals['city']
        
        return city
    
     
class Login_Form(forms.Form):
    email = forms.EmailField(label='Email')
    password=forms.CharField(label="password",widget=forms.PasswordInput(),required=True)    
    
    def clean_password(self):
        vals=self.clean()
        passwd=vals['password']
        if passwd is not None:
            return passwd
        else:
            forms.ValidationError('passwd cannot be empty.')
            
    def clean_email(self):
        vals = self.clean()
        email=vals['email']
        check_pass=False
        if email_re.search(email):
            if(email.find("*") == -1):
                check_pass=True
             
            if(email.find("%") == -1):
                check_pass=True
        
            if(email.find("?") == -1):
                check_pass=True
                    
            if check_pass==False:
                raise forms.ValidationError('email not valid, enter again ')
            return email
        else:
            try:
                User.objects.get(username=email)
                return email
            except User.DoesNotExist:
                raise forms.ValidationError("email not registered")
            
            
class Password_Reset(forms.Form):
    
    email = forms.EmailField(label='Your Email')
    def clean_email(self):
        vals = self.clean()
        email=vals['email']
        check_pass=False
        if email_re.search(email):
            if(email.find("*") == -1):
                check_pass=True
             
            if(email.find("%") == -1):
                check_pass=True
        
            if(email.find("?") == -1):
                check_pass=True
                    
            if check_pass==False:
                raise forms.ValidationError('email not valid, enter again ')
            return email
        else:
            raise forms.ValidationError("email not valid")
        
                   
class EditProfile(forms.Form):
    firstname=forms.CharField(label="First Name",required=False)
    lastname=forms.CharField(label="Last Name",required=False)
    profilepic=forms.ImageField(required=False)
    country=forms.ChoiceField(label="Country",choices=countries,required=False)
    city=forms.CharField(label="City",required=False)
    aboutme=forms.CharField(label="About Me", widget=forms.Textarea,required=False)
    visibility=forms.ChoiceField(label="Profile Visibility",choices=visibility_choices,required=False)
    school=forms.CharField(label="Recent school/college",required=False)
    
    def get_country(self):
        vals=self.clean()
        index=vals['country']
        cname=getcountry(int(index))
        return cname
    def get_visibility(self):
        vals=self.clean()
        index=vals['visibility']
        return index
        
    def get_city(self):
        vals=self.clean()
        return vals['city']
    def get_image(self):
        vals=self.clean()
        return vals['profilepic']   
    def get_aboutme(self):
        vals=self.clean()
        return vals['aboutme']
    def get_school(self):
        vals=self.clean()
        return vals['school']
    def get_firstname(self):
        vals=self.clean()
        return vals['firstname']
    def get_lastname(self):
        vals=self.clean()
        return vals['lastname']
    
class Inviteform(forms.Form):
    invitations=forms.CharField(widget=forms.Textarea)
    def get_invitations(self):
        vals=self.clean()
        emails=vals['invitations'].strip()
        return emails
    
class ChangePassword(forms.Form):
    current_password=forms.CharField(label="Current Password",required=True,widget=forms.PasswordInput())
    password1=forms.CharField(label="New password",required=True,widget=forms.PasswordInput())
    password2=forms.CharField(label="Enter Again",required=True,widget=forms.PasswordInput())
    def get_currentpassword(self):
        vals=self.clean()
        current=vals['current_password'].strip()
        return current
    def checkpassword(self):
        vals=self.clean()
        new1=vals['password1'].strip()
        new2=vals['password2'].strip()
        if (new1 == new2):
            return new1
        else:
            forms.ValidationError("passwords dont match")

class Memoryform(forms.Form):
    #textfield=forms.CharField(label="memory",required=True)
    month=forms.ChoiceField(choices=months_choices,required=False)
    day=forms.ChoiceField(choices=day_choices,required=False)
    year=forms.ChoiceField(choices=getyear(),required=False)
    #filefield=forms.FileField(required=False)        
    