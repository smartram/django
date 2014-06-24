"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from stringroot.settings import MEDIA_ROOT

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

def removefiles():
    import os
    from upload.models import Posts
    delall=Posts.objects.select_related('ownerid__homedir').filter(mark_delete=True)
    for i in delall:
        if i.filename:
            delfile=os.path.join(MEDIA_ROOT , i.ownerid.homedir , "/" , i.filename)
            print "removing %s"%(delfile)
            os.remove(delfile)
        i.delete()
        
def getdim():
    from upload.models import *
    from PIL import Image
    from django.db.models import Q

    import os
    allp=Posts.objects.filter(Q(filetype=7) | Q(filetype=8) | Q(filetype=9))
    for i in allp:
        if i.width is None:
            location=os.path.join(MEDIA_ROOT , i.ownerid.homedir  , i.filename)
            im=Image.open(location)
            i.width,i.height=im.size
            i.save()
    
