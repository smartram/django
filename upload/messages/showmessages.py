'''
Created on Dec 25, 2012

@author: vedara
'''
from upload.models import Messages,DEL_MSGS_TOUSER,DEL_ALL
from stringroot.settings import SITE_MEDIA

MAX_MSGPREVIEW=20

class InboxMessage(object):
    
    fromusername=""
    fromuserimage=""
    shorttext=""
    messageid=0
    def __init__(self):
        self.fromusername=""
        self.fromuserimage=""
        self.shorttext=""
        self.messageid=0


def getTotalUnreadMessages(ownerperson):
    unreadMessages=Messages.objects.filter(to_user=ownerperson).filter(unread=True).count()
    return unreadMessages

def markMessagesasRead(list_msgids):
    Messages.objects.filter(messageid__in=list_msgids).update(unread=False)
    return True
    
def getInboxMessages(ownerperson,startindex=0,endindex=MAX_MSGPREVIEW):
    #get latest message from each user, group by user again.  
    group_messages=Messages.objects.exclude(delmode__in=[DEL_MSGS_TOUSER,DEL_ALL]).filter(to_user=ownerperson).order_by("from_user","-messageid",).distinct("from_user")[startindex:endindex]
    #use insertion sort. get the latest msg from each user. messageid determines the latestone.
    list_messages=[]
    start=True
    
    for msg in group_messages:
        if(start):# first element just insert into list. from 2nd element onwards compare messageid and insert.
            list_messages.append(msg)
            start=False
        else:
            list_index=0
            for emsg in list_messages: # get appropriate location to insert. 
                if msg.messageid > emsg.messageid:
                    list_messages.insert(list_index,msg)
                    break
                list_index=list_index+1
    return list_messages

def InitInboxMessages(ownerperson):
    list_messages=getInboxMessages(ownerperson)
    inbox_msgs=[]
    for msg in list_messages:
        newmsg=InboxMessage()
        newmsg.fromusername=msg.from_user.username
        newmsg.fromuserimage=SITE_MEDIA + msg.from_user.image.name
        newmsg.shorttext=msg.message[0:50]+ "..."
        inbox_msgs.append(newmsg)
    return inbox_msgs

def getnextInboxMessages(owner,startindex,endindex):
    list_messages=getInboxMessages(owner,startindex,endindex)
    inbox_msgs=[]
    for msg in list_messages:
        newmsg=InboxMessage()
        newmsg.fromusername=msg.from_user.username
        newmsg.fromuserimage=SITE_MEDIA + msg.from_user.image.name
        newmsg.shorttext=msg.message[0:50] + "..."
        inbox_msgs.append(newmsg)
    return inbox_msgs


