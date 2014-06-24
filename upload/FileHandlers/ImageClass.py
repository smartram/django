'''
Created on Dec 26, 2012

@author: vedara
'''
from BaseFile import *
from PIL import Image
#from django.utils import timezone
import time
from upload.includes import removespecialchars

class ImageClass(File):
    
    def __init__(self,personobj,homedir,list_filedesc,message,filetype,ismultiple=False):
        self.ismultiple=ismultiple
        self.albumcover="" #consists of filename for image inside of folder album

        File.__init__(self, personobj, homedir, list_filedesc, message, filetype)
        
    
    def save(self):
        dict_post={}
        homedir=self.homedir
        try:
            
            #filename=self.filedesc.name
            
            if self.ismultiple:
                timeasint = int(round(time.time() * 1000))
                timeasstring= str(timeasint)
                album="album"+ removespecialchars(timeasstring)
                parentdir=os.path.join(MEDIA_ROOT,homedir,album)
                os.mkdir(parentdir)
            else:
                parentdir=os.path.join(MEDIA_ROOT ,homedir + sep())
               
            first=True 
            for filedesc in self.list_filedesc:

                filename=filedesc.name     
               
                filename=''.join([x for x in filename if x not in ['[',']','(',')','-','#','$','@','^','&','*','!','+','=','_',',','~','`',"'"]])
                filename=filename.replace(' ','_')
                if len(filename) == 0:
                    filename="".join([choice(string.ascii_lowercase + string.digits) for x in range(9)])       
                path=os.path.join(parentdir, filename)
                     
                if (os.access(path,os.F_OK)): # file already exists
                    newfile=get_uniquename(filename,parentdir)
                    newfile=str(newfile).replace(' ','_')
                    path=os.path.join(parentdir , newfile)
                else:
                    newfile=filename
            
                if first and not self.ismultiple:
                    self.filename=newfile
                elif first and self.ismultiple:
                    self.filename=album #foldername
                    self.albumcover=newfile
                
                    
                dest=open(path.encode('utf-8'),'wb+')
                self.saved_location=path
                self.filesize=0 # give users unlimited space for photos. so just make it 0.
                if filedesc.multiple_chunks:
                    chuncks=filedesc.read(CHUNCK_SIZE)
                    while chuncks!='':
                        dest.write(chuncks)
                        chuncks=filedesc.read(CHUNCK_SIZE)
                else:
                    dest.write(filedesc.read())
                    dest.close()
               
                if first:
                    im=Image.open(self.saved_location)
                    width,height=im.size
                    dict_post['width']=width
                    dict_post['height']=height
                    if self.ismultiple:
                        dict_post['albumcover']=self.albumcover
                    first=False
        
                    
            
            #dict_post['saved_location']=self.saved_location
            if self.ismultiple:
                dict_post['filetype']=allowed_filetypes['folderalbum']
                
            else:
                dict_post['filetype']=self.filetype
            
            dict_post['filename']=self.filename
            dict_post['filesize']=0
            dict_post['status']=0
            
            #if not self.ismultiple:
          
            #log("returning image")    
            return dict_post

        except Exception:
            dict_post['status']=-1
            return dict_post

        
    

