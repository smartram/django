'''
Created on Oct 13, 2012

@author: vedara
'''

'''
from stringroot.settings import VIDEO_DIR,FFMPEG
from BaseFile import *
#from taskq.tasks import convert_to_flv

class VideoClass(File):
    def __init__(self,username,homedir,filedesc,message,filetype=5):
        
        File.__init__(self,username,homedir,filedesc,message,filetype)
    
    #def convert(self,newfile,path,message):
        #convert_to_flv.delay(newfile,path,message,self.username,self.homedir)
        #return True
    
    def save(self):
        #check for hdfs and put it in that dir
        if(HDFS):
            pass # TO DO ADD hdfs apis here.
             
        else:
            filename=self.filedesc.name
            filename.replace('', '_').replace('[','_').replace(']','_')
            if self.homedir==None:
                homedir=""
            else:
                homedir=self.homedir
    
            parentdir=VIDEO_DIR
            
            path=os.path.join(parentdir+ filename)
            #log("path is %s"%(path))
            #log("filename is %s"%(filename))           
            
            if (os.access(path,os.F_OK)): # file already exists
                newfile=get_uniquename(filename,parentdir)
                path=os.path.join(parentdir + newfile)
            else:
                newfile=filename
                
            dest=open(path.encode('utf-8'),'wb+')
            if self.filedesc.multiple_chunks:
                chuncks=self.filedesc.read(CHUNCK_SIZE)
                while chuncks!='':
                    dest.write(chuncks)
                    chuncks=self.filedesc.read(CHUNCK_SIZE)
            else:
                dest.write(self.filedesc.read())
            dest.close()
        
        status=self.convert(newfile,path,self.message)
        dict_post={}
        dict_post['status']=1 # 1 for later. we dont return post now. as conversion is pending
        return status
            
'''    