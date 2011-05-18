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
#Created on Apr 28, 2011
# Joost Horward


"""
Icon View
*********
"""

import gtk
import os
import platform
import stat
import subprocess
import urllib
from cmislib.model import *
from contextmenu import ContextMenu
from constants import *

class IconView():
    '''
    IconView class
    Shows icon view of folder, checked out documents or search results
    '''
    
    def __init__(self,app):    
        menu = gtk.Menu()
        self.app=app
        
                # Default icon for a folder
        self.dir_icon = gtk.gdk.pixbuf_new_from_file ("theme/places/folder.png")
        
        self.store = self.createStore()
        self.widget = gtk.IconView(self.store)
        self.widget.connect('button_press_event', self.onButtonPressEvent)
        self.widget.set_text_column(COL_PATH)
        self.widget.set_pixbuf_column(COL_PIXBUF)
        self.widget.set_tooltip_column(COL_TOOLTIP)
        
        self.widget.set_selection_mode(gtk.SELECTION_MULTIPLE)

        self.widget.connect("item-activated", self.onItemActivated)   
        self.widget.connect('key-press-event',self.onKeyPressEvent)
        
        self.fillStore()     

    def onKeyPressEvent(self,widget,event):
        """
        Respond to keypress in IconView
        """
        # F5
        if event.keyval==65474:
            self.fillStore()
        # Delete             
        elif event.keyval==65535:
            items = self.widget.get_selected_items()
            try:
                self.app.util.delete(items)
            except Exception, e:
                self.app.util.exceptionMessage(e)

    def getMimetypeIcon(self,mimetype):
        """
        Get icon for the given mimetype
        """
        if mimetype:
            iconName=mimetype.replace("/","-")+'.png'
            filePath="theme/mimetypes/"+iconName
            if os.path.exists(filePath):
                return gtk.gdk.pixbuf_new_from_file ("theme/mimetypes/"+iconName)
            else:
                return gtk.gdk.pixbuf_new_from_file ("theme/mimetypes/document.png")
        else:
            return gtk.gdk.pixbuf_new_from_file ("theme/mimetypes/document.png")

    def createStore(self):
        """
        Create icon store
        """
        store = gtk.ListStore(str, gtk.gdk.Pixbuf, bool,str,str,bool)
        store.set_sort_column_id(COL_PATH, gtk.SORT_ASCENDING)
        return store
            
    
    def fillStore(self):
        """
        Fill the icon store
        """
        self.store.clear()

        if self.app.currentDirectory == None:
            return
        self.app.statusbar.pop(1)
        self.app.statusbar.push(1,"Loading ...")
        # Make sure the statusbar text is actually shown
        while gtk.events_pending():
            gtk.main_iteration()
        # Get the working copies if we are in PWC view mode
        if self.app.viewType==VIEW_PWC:
            self.app.set_title("CMIS Navigator [Checked out documents]")
            children=self.app.repo.getCheckedOutDocs()
        # Else get the folder contents
        else:
            self.app.set_title("CMIS Navigator ["+self.app.currentDirectory+']')        
            folder = self.app.repo.getObjectByPath(self.app.currentDirectory)        
            children = folder.getChildren()
        
        # Populate the store with collection children
        for child in children:
            isCheckedOut=False
            
            isDir=child.properties["cmis:baseTypeId"]=="cmis:folder"
            
            nodeType = self.app.repo.getTypeDefinition(child.properties["cmis:objectTypeId"])
            propDefs=nodeType.getProperties()
            
            if not isDir:
                icon=self.getMimetypeIcon(child.properties["cmis:contentStreamMimeType"])
                props=child.getProperties()
                if 'cmis:isVersionSeriesCheckedOut' in props:
                    isCheckedOut=props['cmis:isVersionSeriesCheckedOut']
                if isCheckedOut:
                    toolTip="<b>Document (Checked out)</b>\n"                
                else:
                    toolTip="<b>Document</b>\n"
                for propKey in child.properties:                    
                    #toolTip+=propKey+" : "+str(child.properties[propKey])+"\n"
                    toolTip+=propDefs[propKey].getDisplayName()+" ("+propKey+"): "+str(child.properties[propKey])+"\n"
                                                
            else:
                icon=self.dir_icon                
                props=child.getProperties()

                toolTip="<b>Folder</b>\n"
                for propKey in props:
                    toolTip+=propDefs[propKey].getDisplayName()+" ("+propKey+"): "+str(child.properties[propKey])+"\n"
                
                
            self.store.append([child.name,icon,isDir,toolTip,child.id,isCheckedOut])
        self.app.statusbar.push(1,"Loading ... done.");             
    
    def onItemActivated(self, widget, itemNo):
        """
        Action when item is left-clicked
        """
        model = widget.get_model()
        path = model[itemNo][COL_PATH]
        isDir = model[itemNo][COL_IS_DIRECTORY]
        if not isDir:
            item=[[itemNo]]
            # TODO read only open needs to go to library            
            #self.app.contextMenu.open_read_only(widget,item)
            if self.app.currentDirectory=="/":
                fullPath="/"+path
            else:
                fullPath=self.app.currentDirectory+"/"+path
        
            
            self.app.util.openReadOnly(fullPath)
            return
        
        #self.currentDirectory = self.currentDirectory + os.path.sep + path
        if self.app.currentDirectory=="/":
            self.app.currentDirectory = "/" + path
        else:
            self.app.currentDirectory = self.app.currentDirectory + "/" + path
        self.fillStore()
        self.app.toolbar.upButton.set_sensitive(True)
        
        
    def onButtonPressEvent(self,wid,event):
        
        if event.button==3:
            item = self.widget.get_item_at_pos(int(event.x), int(event.y))
            if item:
                menu = ContextMenu(item,event,self.app)

    