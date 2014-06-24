'''
Created on Sep 6, 2012

@author: vedara
'''
from __future__ import division

from django.core import mail
from django.core.mail import send_mail,EmailMessage

#from django.core.files.base import ContentFile

import threading
import string
import random 
import os
from PIL import  Image
#from taskq.tasks import email_users,send_bulk_emails 
from stringroot.settings import EMAIL_HOST,EMAIL_HOST_USER,EMAIL_HOST_PASSWORD,DEFAULT_FROM_EMAIL
from collections import namedtuple

tempfile="/tmp/logfile.txt"    
    
class Photo:
    def __init__(self,src="",width=0,height=0):
        self.src=src
        self.width=width
        self.height=height
        
def email_user(email_subject,email_body,email):
                                 
    #email_users.delay(email_subject,email_body,email) # dont use celery initially. it takes 25 MB for each process. 
    #tolist.append(email)
    #fail_silently=True
    '''
    t = threading.Thread(target=send_mail,args=(email_subject, email_body, from_account,tolist,fail_silently))
                     
    t.setDaemon(True)
    t.start()
    
    '''
    
    email=EmailMessage(email_subject,email_body,to=[email])
    email.content_subtype="html"
    t = threading.Thread(target=email.send)
    t.setDaemon(True)
    t.start()
    #email.send()

    

def generate_password():
    ran="".join([random.choice(string.letters+string.digits) for x in range(1, 9)])
    return ran

def remove(fpath):
    os.remove(fpath)

def makedir(dpath):
    try:
        os.mkdir(dpath)
        return True
    except Exception:
        return False
    
def save_thumbnail(image_file):
    
    im=Image.open(image_file)
    #im.file.save(image_file,ContentFile(open(image_file).read()))
    im.thumbnail((120, 140), Image.ANTIALIAS)
    im.save(image_file, "JPEG")

'''   
def save_gif(image_file):
    from PIL import  Image
    
    frames = images2gif.readGif("rose.gif",False)
    for frame in frames:
        frame.thumbnail((120,140), Image.ANTIALIAS)

    images2gif.writeGif('rose99.gif', frames)
'''
        
def send_emails(email_list,subject,content):
   
    #email_list=['rao_soft27@yahoo.com','sailaja.cln@gmail.com']
    #send_bulk_emails.delay(email_list,subject,content)
    connection=mail.get_connection()
    connection.open()
    for mailid in email_list:
        msg = EmailMessage(subject, content, DEFAULT_FROM_EMAIL, [mailid])
        #msg = EmailMessage(subject, html_content, from_account, [mailid])
        msg.content_subtype="html" #uncomment in production
        
        connection.send_messages([msg])
    connection.close()
    
        
def get_uniquename(filename,newpath):
    #filename= filename + "_"
    file_fields=filename.split(".")
    if(len(file_fields)==2):
        filename_only="".join(file_fields[0])
    else:
        filename_only="".join(file_fields[0:-1])
    
    ext="." + "".join(file_fields[-1])
    filename_only=filename_only + "_"     
    
    filename=filename_only + ext
    path=os.path.join(newpath + filename)
    
    if (os.access(path, os.F_OK)): # again file exists
        random_letters="".join([random.choice(filename+string.digits) for x in range(1, 4)])
        filename_only=filename_only + random_letters
        filename= filename_only + ext
        return filename
    else:
        return filename
    
def log(message):
    filename=open(tempfile,"a+")
    filename.write(message)
    filename.flush()
    
def sep():
    import sys
    if sys.platform !="win32":
        return "/"
    else:
        return "\\"
 
def which_bitisset(number):
    setbit=1
    if number & setbit ==1:
        return setbit
    for i in xrange(1,32):
        bit=setbit << i
        if bit & number > 0:
            return i+1
    return 0
   
def binarynum(number):
    bit=1
    if number > 1:
        return (0 | (bit << number-1))
    else:
        return 1


def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]
    
def photodim(width,height): # to be deprecated later
    width=width/10
    height=height/10
    
    pfac=width/height
    if pfac == 0:
        pfac=height/width
    if width > 300:
        
        fac=width/100
        width=width/fac
        height=width/pfac
        
    elif height > 300:
        fac=height/100
        height=height/fac
        width=pfac * height
        
    if height < 50:
        height=height + 50
    if width < 50:
        width=width + 50
        
    return (width,height)   

def cropdim(pwidth,pheight,maxWidth=180,maxHeight=180):
    width=newwidth=pwidth
    height=newheight=pheight
    
    if(width > maxWidth):
        ratio = maxWidth / width  # get ratio for scaling image
        height = int(height * ratio)     # Reset height to match scaled image
        width=maxWidth
        newwidth=width
        newheight=height
        # Check if current height is larger than max
        width = int (width * ratio)    # Reset width to match scaled image

    if(height > maxHeight):
        ratio = maxHeight / height #get ratio for scaling image
        height=maxHeight
        width = int  (width * ratio )   # Reset width to match scaled image
        newwidth=width
        
    return newwidth,newheight
        
    
def removespecialchars(s_astring):
    s_astring=s_astring.replace('[', '').replace('(','').replace(')','').replace(']','').replace(' ','').replace('+','').replace('\\','').replace('/','')
    s_astring=s_astring.replace(':','').replace('[','').replace('>','')
    return s_astring

def getphotodesc(parentdir,photoname,factor=160):
    absfile=os.path.join(parentdir,photoname)
    if (os.access(absfile, os.F_OK)==False):
        return None
   
    im=Image.open(absfile)
    width,height=im.size
    photopost=Photo()
    photopost.src=photoname
    photopost.width,photopost.height=cropdim(width,height,factor,factor)
    return photopost
    

def email_inactiveusers():
    import pytz,datetime
    #from django.core.mail import EmailMultiAlternatives

    from django.utils import timezone
    from upload.models import User
    from django.template.loader import render_to_string
    #from django.utils.html import strip_tags


    utc=pytz.timezone("UTC")
    present=timezone.now()
    year=present.year
    month=present.month
    if month == 1:
        year=year -1 
        month=12
    else:
        month=month - 1 
    pastdate=utc.localize(datetime.datetime(year,month,1,1,1))
    uall=User.objects.filter(last_login__lt=pastdate)
    #uall=User.objects.filter(is_active=True)
    print ( "getting list of users who didnt login from %d%d"%(year,month))
    for i in uall:
        email_subject="we are missing you in stringroot"
        email_body=render_to_string('reminder.html', {'username':i.username})
        email=EmailMessage(email_subject,email_body,to=[i.email])
        email.content_subtype= 'html'
        try:
            
            email.send()
        except Exception:
            print "Failed sending Email for Inactive Users %s"%(i.username)
        