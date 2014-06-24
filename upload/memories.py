'''
Created on Dec 2, 2013

@author: venkataedara
'''
from stringroot.settings import SITE_MEDIA
from hexaposts import UserMemory
from upload.models import Memories,get_filetype
import os
from upload.stdincludes import photodim

NUM_MEMORIES=10

def usermemory(db_mem):
    usermem=UserMemory()
    usermem.id=db_mem.id
    if db_mem.filetype == 10:
        usermem.ftype=os.path.join(SITE_MEDIA,db_mem.ownerid.homedir,db_mem.filename,db_mem.albumcover) #here filename is folder name and albumcover is photo name
    elif db_mem.filetype==7 or db_mem.filetype==8 or db_mem.filetype==9:
        usermem.ftype=os.path.join(SITE_MEDIA , db_mem.ownerid.homedir , db_mem.filename)
        
    elif db_mem.filetype is not None and db_mem.filetype in get_filetype:
        usermem.ftype=get_filetype[db_mem.filetype]
    usermem.code=db_mem.code
    usermem.posttype=db_mem.filetype
    usermem.height=db_mem.height
    usermem.width=db_mem.width
    usermem.month=db_mem.month
    usermem.year=db_mem.year
    usermem.day=db_mem.day
    usermem.memtext=db_mem.memtext
    usermem.timestamp=db_mem.timestamp
    if db_mem.width and db_mem.height:
        usermem.width,usermem.height=photodim(db_mem.width,db_mem.height)
       
    return usermem    
def savememory(dict_memory):
    dbmemory=Memories.objects.create(**dict_memory)
    memory=usermemory(dbmemory)    
    return memory    

def getMemoriesbyMonth_DB(ownerid,monthnum,start=0):
    mall=Memories.objects.select_related().filter(ownerid=ownerid).filter(month=monthnum).order_by("-year")[start:start+NUM_MEMORIES]
    return mall
def getMemoriesbyYear_DB(ownerid,yearnum,start=0):
    mall=Memories.objects.select_related().filter(ownerid=ownerid).filter(year=yearnum).order_by("month")[start:start+NUM_MEMORIES]
    return mall

def getMemoriesbyMonth(ownerid,monthnum,start=0):
    mall=getMemoriesbyMonth_DB(ownerid,monthnum,start)
    mall=[usermemory(m) for m in mall]
    return mall
        