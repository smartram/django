'''
Created on Oct 13, 2012

@author: vedara
'''
from upload.models import *
from BaseFile import *

class PdfClass(File):
        
    def __init__(self,username,homedir,filedesc,message,filetype):
        
        File.__init__(self,username,homedir,filedesc,message,filetype)
    
            
        