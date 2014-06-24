'''
Created on Oct 13, 2012

@author: vedara
'''
from BaseFile import *

class Mp3Class(File):
    '''
    classdocs
    '''


    def __init__(self,username,homedir,filedesc,message,filetype):
    
    #    Constructor
     
        File.__init__(self,username,homedir,filedesc,message,filetype)