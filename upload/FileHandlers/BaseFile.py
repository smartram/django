'''
Created on Oct 13, 2012

@author: vedara
'''

from upload.includes import get_uniquename,log,sep
from upload.models import *
from random import choice
from django.core.cache import cache

from stringroot.settings import MEDIA_ROOT
import os,datetime 
import string

CHUNCK_SIZE=4096 # 4 kb

    
class File(object):
    
    def __init__(self,personobj,homedir,list_filedesc,message,filetype):
        
        self.username=personobj.username
        self.personobj=personobj
        self.list_filedesc=list_filedesc
        self.homedir=homedir
        self.filetype=filetype
        self.filesize=0
        self.saved_location=""
        self.message=message
        self.filename=""
   
    def writedb(self):
        dict_post={}
        now=str(datetime.datetime.today()).split(" ")
        now=str(now[1]).replace(':','1').replace('.', '1')
            #random_code="%s%s%s"%(newfile,self.username,now)
            #random_code=random_code.replace('[', '').replace('(','').replace(')','').replace(']','').replace(' ','')
        uniqcode="".join([choice(self.filename + now ) for x in range(9)])
        uniqcode=uniqcode.replace('.','_')
        timestamp=timezone.now()

        post=Posts.objects.create(text=self.message,filename=self.filename,ownerid=self.personobj,
                                  filetype=self.filetype,code=uniqcode,filesize=self.filesize,timestamp=timestamp)
        Hits.objects.create(postcode=post,hits=0)
        dict_post['status']=0 # 0 for uploaded posts . we return now itself
        dict_post['post']=post    
        dict_post['filesize']=int(self.filesize/1048576)
            
        return dict_post
   
    def save(self):
        #check for hdfs and put it in that dir
        dict_post={}
        filedesc=self.list_filedesc[0] # upload only 1st file
        
        try:
            filename=filedesc.name
            filename=''.join([x for x in filename if x not in ['[',']','(',')','-','#','$','@','^','&','*','!','+','=','_',',','~','`',"'"]])
            filename=filename.replace(' ','_')
            if len(filename) == 0:
                filename="".join([choice(string.ascii_lowercase + string.digits) for x in range(9)])       
            homedir=self.homedir
            parentdir=os.path.join(MEDIA_ROOT ,homedir + sep())
            path=os.path.join(parentdir, filename)
                 
            if (os.access(path,os.F_OK)): # file already exists
                newfile=get_uniquename(filename,parentdir)
                newfile=str(newfile).replace(' ','_')
                path=os.path.join(parentdir , newfile)
            else:
                newfile=filename
            
            self.filename=newfile
            dest=open(path.encode('utf-8'),'wb+')
            self.saved_location=path
            self.filesize=filedesc.size
            if filedesc.multiple_chunks:
                chuncks=filedesc.read(CHUNCK_SIZE)
                while chuncks!='':
                    dest.write(chuncks)
                    chuncks=filedesc.read(CHUNCK_SIZE)
            else:
                dest.write(filedesc.read())
                dest.close()
            
            dict_post['filetype']=self.filetype
            dict_post['filesize']=self.filesize
            dict_post['filename']=self.filename
            dict_post['filesize']=int(self.filesize/1048576)

            dict_post['status']=0
            return dict_post
        
            
        except Exception:
            dict_post['status']=-1
            dict_post['html']="<p> error occurred when uploding, please try again </p>"
            return dict_post
