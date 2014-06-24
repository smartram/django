'''
Created on Oct 13, 2012

@author: vedara
'''
from PdfClass import *
from PptClass import *
from ImageClass import *
#from Mp3Class import *
from VideoClass import *
from upload.includes import log
from upload.models import allowed_filetypes


#allowed_extensions=[".pdf","pdf",".ppt","ppt",".flv","flv",".mp3","mp3","jpeg","jpg",".jpg",".jpeg","png",".png","gif",".gif"]
allowed_extensions=allowed_filetypes.keys()

def handle_uploads(list_fileobj,message,personobj,homedir):
    isalbum=False
    numoffiles=len(list_fileobj)
    numofimages=0
    
    
    dict_postobj={}
    dict_postobj['status']=-1
   
    #check if album or not .
    for fileobj in list_fileobj:
        file_fields=str(fileobj.name).split(".")
        log(fileobj.name)
        extension=str(file_fields[-1]).lower()
        if extension in ['.jpeg','jpeg','.jpg','jpg','gif','.gif','png','.png']:
            numofimages=numofimages+1
        
       
    if numofimages==numoffiles and numoffiles > 1:# it is album of photos
        isalbum=True       
        isimage=True
    else:# may be mixed filetypes, dont encourage this . just take 1st file only
        fileobj=list_fileobj[0]
        file_fields=str(fileobj.name).split(".")
        extension=str(file_fields[-1]).lower()
        
        list_fileobj=[fileobj] # just upload only 1st element
        if extension in ['.jpeg','jpeg','.jpg','jpg','gif','.gif','png','.png']:
            isimage=True
        elif extension in allowed_extensions:
            isimage=False
        else:
            return dict_postobj    
        
    if isimage:
        Imageobj=ImageClass(personobj,homedir,list_fileobj,message,allowed_filetypes[extension],isalbum)
        dict_postobj=Imageobj.save()
            #dict_postobj=Imageobj.writedb()
        return dict_postobj
    
    elif not isimage and extension in allowed_extensions:
        filetype=allowed_filetypes[extension]
        Fileobj=File(personobj,homedir,list_fileobj,message,filetype)
        dict_postobj=Fileobj.save()
        #dict_postobj=Fileobj.writedb()
        return dict_postobj
        #log(extension)
    else:
        dict_postobj["status"]=-1
        dict_postobj["html"]="<p> cannot upload different filetypes at a time </p>"
        return dict_postobj
    
