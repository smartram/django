'''
Created on Jul 6, 2013

@author: venkataedara
'''

'''
from celery import Celery

celery = Celery('tasks', broker='amqp://guest@localhost//')

@celery.task
'''
from django.db.models import F
from upload.models import Posts,Hits
def save_hits_todb(postcode):
    Hits.objects.filter(postcode__code=postcode).update(hits=F('hits')+1)