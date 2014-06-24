'''
Created on Apr 24, 2013

@author: venkataedara
'''
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.shortcuts import render_to_response,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.template import RequestContext
from django.template.loader import *


from django.core.urlresolvers import reverse
from django.contrib.auth import *

from forms import *
from upload.models import *
from upload.includes import *
from upload.emailauth import *

from stringroot.settings import STATIC_URL,STATIC_ROOT,MEDIA_ROOT
import sha,datetime
from upload.friends import *

import os,re
from django.utils import simplejson
from upload.FileHandlers.handle_uploads import * 
from upload.hexaposts import *
