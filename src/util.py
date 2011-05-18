#
# CMIS Navigator
# Copyright 2011, Open-T B.V., and individual contributors as indicated
# by the @author tag. See the copyright.txt in the distribution for a
# full listing of individual contributors.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License
# version 3 published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses
#
# Created on Apr 28, 2011
# Joost Horward

"""
Util
****
Provides utility functions used throughout the Navigator
"""

import gtk
import os
import subprocess
import stat
from cmislib.model import *

class Util():
    def __init__(self,app):
        self.app=app
    
    def errorMessage(self,message):
        """
        Display an error message dialog box        
        
        **Args:**
            message(str): The message to be shown        
        """
        dialog = gtk.MessageDialog(
        parent         = None,
        flags          = gtk.DIALOG_DESTROY_WITH_PARENT,
        type           = gtk.MESSAGE_ERROR,
        buttons        = gtk.BUTTONS_OK,        
        message_format=message)
        
        dialog.set_title('Error')
        #dialog.connect('response', self.on_drop)
        dialog.show()
        dialog.run()
        dialog.hide()
        
    def delete(self,items):
        """
        Deletes the items in the list        
        **Args:**
            items(array): The IconView selection to be deleted
        """
        for item in items:
            itemNo=item[0]
            itemName=self.app.iconView.store[itemNo][0]
            nodeRef=self.app.iconView.store[itemNo][4]     
            message = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, "Are you sure you want to delete "+itemName+" ?")
            response= message.run()
            message.destroy()
            if response == gtk.RESPONSE_OK:
                self.app.statusbar.push(1,"Deleting "+ itemName)
                fileNode = self.app.repo.getObject(nodeRef)
                fileNode.delete()
                self.app.iconView.fillStore()
            else:
                self.app.statusbar.push(1,itemName+" deleted.")
    
    def openReadOnly(self,fullPath):
        """
        Open the file read-only        
        **Args:**
            fullPath(str): The path to the file to be opened
                
        """
        fileNode= self.app.repo.getObjectByPath(fullPath)
        localFilePath=self.app.config.get("paths","local")+"/"+self.app.repo.id+fullPath
        localDirPath=os.path.dirname(localFilePath)
        if os.path.exists(localDirPath)==False:
            os.makedirs(localDirPath)
        if os.path.exists(localFilePath):
            os.chmod(localFilePath, stat.S_IREAD + stat.S_IWRITE)
        
        o = open(localFilePath, 'wb')
        result = fileNode.getContentStream()
        o.write(result.read())
        result.close()
        o.close()
        os.chmod(localFilePath, stat.S_IREAD)
        
        subprocess.Popen([self.app.config.get('programs','open'),localFilePath])


    def statusMessage(self,statusMessage):
        self.app.statusbar.push(1,statusMessage)
        while gtk.events_pending():
            gtk.main_iteration()
    def exceptionMessage(self,e):
        self.errorMessage("An exception occurred.\n The exception string is: "+str(e))        
            
    def localRepoPath(self):
        return self.app.config.get("paths","local")+"/"+self.app.repo.id
    
    
    def getProps(self,node,propType):
        props={}
        propElements = node.getElementsByTagNameNS(CMIS_NS, propType)
        for el in propElements:
            propertyId=el.attributes['propertyDefinitionId'].value
            displayName= el.attributes['displayName'].value            
            vals=el.getElementsByTagNameNS(CMIS_NS, 'value')
            value=None            
            if len(vals)>0:
                if len(vals[0].childNodes)>0:
                    value= vals[0].childNodes[0].data
            props[propertyId]= {"propertyId":propertyId,"displayName":displayName,"value":value,"type":propType}
        return props