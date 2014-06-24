'''
Created on Oct 13, 2012

@author: vedara
'''
from BaseFile import *

class PPTClass(File):
    

    '''
    classdocs
    '''


    def __init__(self,username,homedir,filedesc,message,filetype):
        
        File.__init__(self,username,homedir,filedesc,message,filetype)     