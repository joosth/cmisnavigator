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
Context menu
************
Provides a context menu for the IconView
"""



import gtk
import os
import subprocess
import urllib
import stat
from cmislib.model import *
from constants import *


class ContextMenu():
    """
    Implements the context menu for the icon view
    It is created at the time the user hits right-mouse
    So it can dynamically respond to the actual situation at construction time
    """
    
    def __init__(self,item,event,app):    
        menu = gtk.Menu()
        self.app=app
        
        itemNo=item[0][0]
        
        itemName=self.app.iconView.store[itemNo][COL_PATH]                
        isDir=self.app.iconView.store[itemNo][COL_IS_DIRECTORY]
        nodeRef=self.app.iconView.store[itemNo][COL_NODEREF]
        isCheckedOut=self.app.iconView.store[itemNo][COL_IS_CHECKED_OUT]
        
        # Open read-only item is only for files
        if not isDir:
            openReadOnlyItem = gtk.MenuItem(label="Open read-only")
            menu.append(openReadOnlyItem)
            openReadOnlyItem.connect("activate",self.onOpenReadOnly,item)
            
        
        # Checkout & edit for browse view of non-checked out files (not folders)
        if self.app.viewType==VIEW_BROWSE and not isCheckedOut and not isDir:        
            checkoutEditItem = gtk.MenuItem(label="Checkout & edit")
            menu.append(checkoutEditItem)
            checkoutEditItem.connect("activate",self.onCheckoutEdit,item)
        
        # Check in on PWC or original document that is checked out
        if self.app.viewType==VIEW_PWC or isCheckedOut:            
            editItem = gtk.MenuItem(label="Edit working copy")
            menu.append(editItem)
            editItem.connect("activate",self.onEditItem,item)
            
            checkinItem = gtk.MenuItem(label="Check in")
            menu.append(checkinItem)
            checkinItem.connect("activate",self.onCheckinItem,item)
        
        # Delete
        delete_item = gtk.MenuItem(label="Delete")
        menu.append(delete_item)
        delete_item.connect("activate",self.onDeleteItem,item)
        
        # Show CMIS XML
        cmisXmlItem = gtk.MenuItem(label="Show CMIS XML")
        menu.append(cmisXmlItem)   
        cmisXmlItem.connect("activate",self.onShowCmisXml,item)
        
        # Edit metadata
        editMetadata = gtk.MenuItem(label="Edit metadata...")
        menu.append(editMetadata)   
        editMetadata.connect("activate",self.onEditMetadata,item)
   
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)
    
    
     
    def onCheckinItem(self,widget,item):        
        """Check in an item. This can happen on a checked-out node or a working copy.
        
        **Args:**
            widget (str): The widget that sent the event
        """
        itemNo=item[0][0]
        
        itemName=self.app.iconView.store[itemNo][COL_PATH]
        
        nodeRef=self.app.iconView.store[itemNo][COL_NODEREF]    
        node = self.app.repo.getObject(nodeRef)
        
        if nodeRef == node.getProperties()['cmis:versionSeriesId']:
            # Node is the original node
            originalNodeRef = nodeRef
            originalNode=node
            checkedOutNode=originalNode.getPrivateWorkingCopy()
            checkedOutNodeRef=checkedOutNode.id            
        else:
            # Node is the checked out node
            checkedOutNodeRef=nodeRef
            checkedOutNode = node
            originalNodeRef = checkedOutNode.getProperties()['cmis:versionSeriesId']
            originalNode=self.app.repo.getObject(originalNodeRef)               

        
        self.checkInDialog = self.app.wTree.get_widget("checkInDialog")
        self.checkInDialog.set_title("Check in "+originalNode.name)


        self.checkInDialog.show()
        result=self.checkInDialog.run()
        self.checkInDialog.hide()
        
        if result==1:
            buf=self.app.wTree.get_widget("checkInCommentTextView").get_buffer()
            start, end = buf.get_bounds()
            checkInComment=buf.get_text(start,end,True)
            
            majorVersion=self.app.wTree.get_widget("majorVersionCheckButton").get_active()
            if majorVersion:
                majorVersionString="true"
            else:
                majorVersionString="false"

            pwcDir=urllib.quote(checkedOutNode.id, "")
            localFilePath=self.app.config.get("paths","checkedout")+"/"+self.app.repo.id+"/"+pwcDir+"/"+originalNode.name        
            if os.path.exists(localFilePath):                
                f=open(localFilePath,"rb")
                checkedOutNode.setContentStream(f)                            
                checkedOutNode.checkin(checkinComment=checkInComment,major=majorVersionString)
            else:                
                node.checkin(checkinComment=checkInComment,major=majorVersionString)
        self.app.iconView.fillStore()
        
    def onEditItem(self,widget,item):
        """Edit an item
        
        Args:
            widget: The widget that sent the signal.            
            
            item: The item in the IconView.

        """
        itemNo=item[0][0]        
        itemName=self.app.iconView.store[itemNo][COL_PATH]
        
        nodeRef=self.app.iconView.store[itemNo][4]    
        node = self.app.repo.getObject(nodeRef)
        
        if nodeRef == node.getProperties()['cmis:versionSeriesId']:
            # Node is the original node
            originalNodeRef = nodeRef
            originalNode=node
            checkedOutNode=originalNode.getPrivateWorkingCopy()
            checkedOutNodeRef=checkedOutNode.id            
        else:
            # Node is the checked out node
            checkedOutNodeRef=nodeRef
            checkedOutNode = node
            originalNodeRef = checkedOutNode.getProperties()['cmis:versionSeriesId']
            originalNode=self.app.repo.getObject(originalNodeRef)            
        pwcDir=urllib.quote(checkedOutNodeRef, "")
        
        localFilePath=self.app.config.get("paths","checkedout")+"/"+self.app.repo.id+"/"+pwcDir+"/"+originalNode.name
        localDirPath=self.app.config.get("paths","checkedout")+"/"+self.app.repo.id+"/"+pwcDir                    
        if not os.path.exists(localDirPath):
            os.makedirs(localDirPath)
        if not os.path.exists(localFilePath):
            o = open(localFilePath, 'wb')
            result = checkedOutNode.getContentStream()
            o.write(result.read())
            result.close()
            o.close()
        subprocess.Popen(["/usr/bin/xdg-open",localFilePath])
        self.app.iconView.fillStore()        
    
    
    def onDeleteItem(self,widget,item):
        """Delete an item
        TODO implement multiple delete using list like below
        items=self.app.iconView.get_selected_items()        
        """
        
        itemNo=item[0][0]
        itemName=self.app.iconView.store[itemNo][COL_PATH]
        nodeRef=self.app.iconView.store[itemNo][COL_NODEREF]        

        # Confirmation dialog        
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


    def onShowCmisXml(self,widget,item):
        """
        Show CMIS XML in a dialog
        """        
        itemNo=item[0][0]
        
        # Get the node        
        nodeRef=self.app.iconView.store[itemNo][COL_NODEREF]    
        node = self.app.repo.getObject(nodeRef)
        
        # Get the Glade dialog
        self.cmisXMLDialog = self.app.wTree.get_widget("cmisXMLDialog")
        buf=self.app.wTree.get_widget("cmisXMLTextView").get_buffer()
        buf.set_text(node.xmlDoc.toxml())

        # Show the dialog
        self.cmisXMLDialog.show()
        self.cmisXMLDialog.run()
        self.cmisXMLDialog.hide()
        
    def getProps(self,node,propType):
        props={}
        propElements = node.getElementsByTagNameNS(CMIS_NS, propType)
        for el in propElements:
            propertyId=el.attributes['propertyDefinitionId'].value
            displayName= el.attributes['displayName'].value            
            vals=el.getElementsByTagNameNS(CMIS_NS, 'value')
            value=None            
            if len(vals)>0:
                value= vals[0].childNodes[0].data
            props[propertyId]= {"propertyId":propertyId,"displayName":displayName,"value":value,"type":propType}
        return props
    
    def onEditMetadata(self,widget,item):
        """
        Edit the node's metadata
        """
        itemNo=item[0][0]
        itemName=self.app.iconView.store[itemNo][COL_PATH]
        nodeRef=self.app.iconView.store[itemNo][COL_NODEREF]    
        node = self.app.repo.getObject(nodeRef)
        
        nodeType = self.app.repo.getTypeDefinition(node.properties["cmis:objectTypeId"])

        propDefs=nodeType.getProperties()
        self.editMetadataDialog = self.app.wTree.get_widget("metadataDialog")        
        
        p={}
        self.metadataTable = gtk.Table(len(propDefs), 2, True);
        
        propertiesElement = node.xmlDoc.getElementsByTagNameNS(CMIS_NS, 'properties')[0]
        
        prps={}
        prps.update(self.app.util.getProps(propertiesElement,"propertyInteger"))
        prps.update(self.app.util.getProps(propertiesElement,"propertyString"))
        prps.update(self.app.util.getProps(propertiesElement,"propertyBoolean"))
        prps.update(self.app.util.getProps(propertiesElement,"propertyId"))
        prps.update(self.app.util.getProps(propertiesElement,"propertyDateTime"))
        
        
        
        n=0
        for propertyId in prps:
            prop=prps[propertyId]
            label=gtk.Label(prop["displayName"])
            label.set_alignment(0,0)
            self.metadataTable.attach(label, 0, 1, n, n+1)            
            
            p[propertyId]=gtk.Entry()
            p[propertyId].set_text(str(prop["value"]))
            self.metadataTable.attach(p[propertyId], 1, 2, n, n+1)
            p[propertyId].set_sensitive(False)
            if propertyId in propDefs:
                if propDefs[propertyId].updatability=="readwrite":
                    p[propertyId].set_sensitive(True)
            n+=1                
        self.metadataTable.show()
        
        if len (self.editMetadataDialog.vbox.get_children())>1:
            self.editMetadataDialog.vbox.remove(self.editMetadataDialog.vbox.get_children()[0])
        self.editMetadataDialog.vbox.add(self.metadataTable)
        

        self.editMetadataDialog.set_title("Edit metadata of "+itemName)
        self.editMetadataDialog.show_all() 
        self.editMetadataDialog.show()        
        result=self.editMetadataDialog.run()                
        self.editMetadataDialog.hide()
        
        # Update the properties if OK was chosen
        props={}
        if result==1:
            for propertyId in p:
                if propertyId in propDefs:
                    if propDefs[propertyId].updatability=="readwrite":                        
                        props[propertyId]=p[propertyId].get_text()                
            node.updateProperties(props)
            self.app.iconView.fillStore()
        
        
    
        
    def onOpenReadOnly(self,event,item):
        """
        Open the file read only
        """
        itemNo=item[0][0]
        itemName=self.app.iconView.store[itemNo][COL_PATH]
        
        # Figure out what the full path of the item is
        if self.app.currentDirectory=="/":
            file="/"+itemName
        else:
            file=self.app.currentDirectory+"/"+itemName
            
        fileNode = self.app.repo.getObjectByPath(file)
        
        localFilePath=self.app.config.get("paths","local")+"/"+self.app.repo.id+file
        localDirPath=os.path.dirname(localFilePath)
        if not os.path.exists(localDirPath):
            os.makedirs(localDirPath)
        if os.path.exists(localFilePath):
            os.chmod(localFilePath, stat.S_IREAD + stat.S_IWRITE)
        
        o = open(localFilePath, 'wb')
        result = fileNode.getContentStream()
        o.write(result.read())
        result.close()
        o.close()
        os.chmod(localFilePath, stat.S_IREAD)
        #self.config.get('programs','open')
        #subprocess.Popen(["/usr/bin/xdg-open",localFilePath])
        subprocess.Popen([self.app.config.get('programs','open'),localFilePath])
        
    def onCheckoutEdit(self,event,item):
        """
        Check out and edit an item        
        """
        itemNo=item[0][0]
        itemName=self.app.iconView.store[itemNo][COL_PATH]

        #Figure out what the full path to the node is
        if self.app.currentDirectory=="/":
            file="/"+itemName
        else:
            file=self.app.currentDirectory+"/"+itemName

        fileNode = self.app.repo.getObjectByPath(file)
        
        # Don't check it out again if it was already checked out
        if not fileNode.isCheckedOut():
            fileNode.checkout()
        pwc=fileNode.getPrivateWorkingCopy()

        # Determine local path to PWC and PWC directory
                
        pwcDir=urllib.quote(pwc.id, "")        
        localFilePath=self.app.config.get("paths","checkedout")+"/"+self.app.repo.id+"/"+pwcDir+"/"+fileNode.name
        localDirPath=self.app.config.get("paths","checkedout")+"/"+self.app.repo.id+"/"+pwcDir
        
        # Create the directory for the PWC if needed
        if not os.path.exists(localDirPath):
            os.makedirs(localDirPath)
        # Fetch the PWC if needed
        if not os.path.exists(localFilePath):
            o = open(localFilePath, 'wb')
            result = fileNode.getContentStream()
            o.write(result.read())
            result.close()
            o.close()
        
        # Repaint the icon view
        self.app.iconView.fillStore()
        
        # Go edit the PWC
        subprocess.Popen([self.app.config.get('programs','open'),localFilePath])
