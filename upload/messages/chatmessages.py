'''
Created on Dec 28, 2012

@author: vedara
'''
from upload.models import Messages,DEL_MSGS_FROMUSER,DEL_MSGS_TOUSER,DEL_ALL
from stringroot.settings import SITE_MEDIA

MAXMSGS=50
class ChatMessages(object):
    fromusername=""
    fromuserimage=""
    text=""
    fromme=False
    timestamp=""
    messageid=""
    unread=False
    
    def __init__(self):
        self.fromme=False
        self.fromuserimage=""
        self.fromusername=""
        self.text=""
        self.timestamp=""
        self.messageid=""
        
def getChatMessages(fromperson,toperson,startindex=0,endindex=MAXMSGS):
    group_messages=Messages.objects.exclude(delmode=DEL_ALL).filter(from_user__in=[fromperson,toperson],to_user__in=[fromperson,toperson]).order_by("-messageid")[startindex:endindex]
    return group_messages

def initChatMessages(ownerperson,toperson):
    list_messages=getChatMessages(ownerperson,toperson)
    chat_messages=[]
    for msg in list_messages:
        cmsg=ChatMessages()
        cmsg.messageid=msg.messageid
        if msg.from_user.username == ownerperson.username:
            cmsg.fromme=True
            cmsg.text=msg.message
            cmsg.timestamp=msg.timestamp
            
        else:
            cmsg.fromuserimage=SITE_MEDIA + msg.from_user.image.name
            cmsg.fromusername=msg.from_user.username
            cmsg.text=msg.message
            cmsg.timestamp=msg.timestamp
            cmsg.unread=msg.unread
        chat_messages.insert(0,cmsg)# inserting at head reverses the list.we need latest msgs at bottom of div
    
    return chat_messages
    
def getprevChatMessages(ownerperson,toperson,startindex,endindex):
    list_messages=getChatMessages(ownerperson,toperson,startindex,endindex)
    chat_messages=[]
    for msg in list_messages:
        cmsg=ChatMessages()
        cmsg.messageid=msg.messageid
        if msg.from_user == ownerperson:
            cmsg.fromme=True
            cmsg.text=msg.message
        else:
            cmsg.fromuserimage=SITE_MEDIA + toperson.image.name
            cmsg.fromusername=toperson.username
            cmsg.text=msg.message
            cmsg.timestamp=msg.timestamp
            cmsg.unread=msg.unread
        chat_messages.insert(0,cmsg)# inserting at head reverses the list.we need latest msgs at bottom of div
    list_messages=[]
    return chat_messages
    
def getlatestchat(frompersonobj,ownerobj,latestchatid):
    latestid=latestchatid
    group_messages=Messages.objects.filter(from_user=frompersonobj,to_user=ownerobj).filter(messageid__gt=latestid).order_by("-messageid")[0:10]
    list_messages=[]
    
    for msg in group_messages:
        cmsg=ChatMessages()
        cmsg.messageid=msg.messageid
        cmsg.text=msg.message
        cmsg.timestamp=msg.timestamp
        list_messages.append(cmsg)
        
    return list_messages

def mark_ids_asread(set_ids):
    Messages.objects.filter(messageid__in=set_ids).update(unread=False)
    return True
    
def create_chatmsg(owner,toperson,msgtext):
    dbChatMessage=Messages()
    dbChatMessage.from_user=owner
    dbChatMessage.to_user=toperson
    dbChatMessage.message=msgtext
    dbChatMessage.save()
    cmsg=ChatMessages()
    cmsg.fromme=True
    cmsg.text=msgtext
    return [cmsg] #returning list


def deletemessages(fromusername,tousername):
    from django.db import connection
    cursor=connection.cursor()
    try:
        #mall=list(Messages.objects.select_related("from_user__username").exclude(delmode=DEL_ALL).filter(from_user__username__in=[fromusername,tousername]).filter(to_user__username__in=[fromusername,tousername]))
        #delmode_fromuser=[x.delmode|DEL_MSGS_FROMUSER for x in mall if x.from_user__username==fromusername]
        #delmode_touser=[x.delmode|DEL_MSGS_TOUSER for x in mall if x.from_user__username == tousername]
        rawquery="UPDATE upload_messages set delmode=delmode|%d where from_user_id='%s' and to_user_id='%s' "%(DEL_MSGS_FROMUSER,fromusername,tousername)
        cursor.execute(rawquery)
        rawquery2="UPDATE upload_messages set delmode=delmode|%d where from_user_id='%s' and to_user_id='%s'"%(DEL_MSGS_TOUSER,tousername,fromusername)
        #Messages.objects.filter(from_user__username__in=[username1,username2],to_user__username__in=[username1,username2]).delete()
        cursor.execute(rawquery2)
        
    except Exception:
        return False
    
    #connection.close()
    return True
