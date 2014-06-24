'''
Created on Dec 15, 2012

@author: vedara
'''
from upload.models import Comments
from stringroot.settings import SITE_MEDIA

class comments(object):
  
    def __init__(self,image="",username="",text=""):
        self.image=image
        self.username=username
        self.text=text
        self.commentid=0
    
    
    
def getcomments(postid):
    allcomments=Comments.objects.filter(postid=postid).filter(is_spam=False).order_by("-commentid")[0:50]
    list_comments=[createcomments(x) for x in allcomments]
    return list_comments

def createcomments(comment):
    new_comment=comments()
    new_comment.image=SITE_MEDIA + comment.user.image.name
    new_comment.username=comment.user.username
    new_comment.text=comment.comment
    new_comment.commentid=comment.commentid
    return new_comment

def postcomment(postid,comment_text,personid):
    newcomment=Comments.objects.create(postid=postid,comment=comment_text,user=personid)
    user_comment=comments()
    user_comment.username=newcomment.user.username
    user_comment.image=SITE_MEDIA + personid.image.name
    user_comment.text=comment_text
    user_comment.commentid=newcomment.commentid
    return user_comment
    
def markasspam(cid):
    count=Comments.objects.filter(commentid=cid).update(is_spam=True)
    return count
