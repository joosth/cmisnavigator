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
Drag and drop for icon view
***************************
"""

import gtk
import gtk.gdk
import os
import platform
import stat
import subprocess
import urllib
import shutil
from cmislib.model import *
from constants import *
class DragDrop():
    """
    Drag and drop functionality
    """
    
    def __init__(self,app):    
        menu = gtk.Menu()
        self.app=app
        
        # For repo to repo we only support move (see dragrop.py)
        self.app.iconView.widget.enable_model_drag_source(0,[('cmis/'+self.app.repo.id, 0, 0),('text/uri-list', 0, 1)], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        #self.app.iconView.widget.drag_source_set(gtk.gdk.BUTTON1_MASK, [('cmis/'+self.app.repo.id, 0, 0),('text/uri-list', 0, 1)],gtk.gdk.ACTION_MOVE)

        # for local to/from repo we only support copy (just to be safe)
        self.app.iconView.widget.enable_model_drag_dest([('cmis/'+self.app.repo.id, 0, 0),('text/uri-list', 0, 1)], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)

        self.app.iconView.widget.connect('drag_data_received', self.onDragDataReceived)
        self.app.iconView.widget.connect("drag_data_get", self.onDragDataGet)
        self.app.iconView.widget.connect("drag_end", self.onDragEnd)
        self.app.iconView.widget.connect("drag_begin", self.onDragBegin)
        self.app.iconView.widget.connect("drag_data_delete", self.onDragDataDelete)

        #self.app.iconView.connect('drag_drop', self.on_drag_drop)

    def uploadRecursive(self,folder,path):
        props={}
        fnameparts=path.split("/")
        fname=fnameparts[len(fnameparts)-1]

        if not os.path.isdir(path):
            self.app.util.statusMessage("Uploading "+path)
            f=open(path,"rb")
            folder.createDocument(fname,props,f)
            self.app.statusbar.push(1,"File "+fname+" uploaded.");
            while gtk.events_pending():
                gtk.main_iteration()
            f.close()
        else:
            self.app.util.statusMessage("Creating folder "+path)            
            newFolder=folder.createFolder(fname)
            children=os.listdir(path)                
            for child in children:                
                self.uploadRecursive(newFolder,path+"/"+child)
        self.app.util.statusMessage("Upload completed.")
        
    def onDragDataReceived(self,wid, context, x, y, selection, info,time):
        """
        Respond to drag data received event
        Performs move or copy operation
        
        .. warning::
            This code still has the following limitations:
        
            * Folders are not copied from/to a a local filesystem because we haven't completed the code yet
            * Copying within the same repository doesn't work yet because createDocumentFromSource is not implemented by cmislib

        """
        
        items=wid.get_selected_items()        
        dropinfo = self.app.iconView.widget.get_dest_item_at_pos(x, y)
        
        if dropinfo!=None:
            itemNo=dropinfo[0][0]
            self.app.itemName=self.app.iconView.store[itemNo][COL_PATH]
            self.app.drop_folder=self.app.currentDirectory+"/"+self.app.itemName
            
        else:
            self.app.itemName=self.app.currentDirectory
            self.app.drop_folder=self.app.itemName

        uris=selection.get_uris()

        droppedString=selection.data[0:len(selection.data)-2]
        droppedNames=droppedString.split("\r\n")
        folder = self.app.repo.getObjectByPath(self.app.drop_folder)
        props = {}
        
        if info==1:
            for droppedName in droppedNames:
                if platform.system()=="Windows":
                    droppedName=droppedName.replace("file:///","").replace("%20"," ").replace("\r","")
                else:
                    droppedName=droppedName.replace("file://","").replace("%20"," ").replace("\r","")                 
                self.uploadRecursive(folder, droppedName)             
        else:
            # Internal copy or move                          
            for uri in uris:
                filePath=uri.replace("cmis://","")
                dirPath=os.path.dirname(filePath)
                sourceFolder=self.app.repo.getObjectByPath(dirPath)
                destFolder=self.app.repo.getObjectByPath(self.app.drop_folder)                    
                node=self.app.repo.getObjectByPath(filePath)
                if context.action == gtk.gdk.ACTION_MOVE:
                    # move node        
                    node.move(sourceFolder,destFolder)
                if context.action == gtk.gdk.ACTION_COPY:
                    # TODO copy node - doesn't work properly yet
                    self.app.util.errorMessage("Repo to repo copy not supported yet (only move is supported at this time).")
                    #self.app.repo.createDocumentFromSource(node.id,{},destFolder)                    
                    # This would create a hard link rather than a copy
                    #destFolder.addObject(node)                            
        self.app.iconView.fillStore()
        context.drop_finish(True)    
        
        
    def onDragDataGet(self, iconView, context, selection, target_id,etime):
        """
        This is called when we are the source of the D&D
        It gives us a chance to prepare
        and to create a local copy if needed
        Hands back selected items in selection
        The target ID is the chosen target (0=CMIS URI of same repository, 1=Normal URI)
        """        
        
        if self.newDrag:
            
            self.dragSelection=selection
            self.dragItems=self.app.iconView.widget.get_selected_items()
            self.dragTargetId=target_id
            
            items=self.app.iconView.widget.get_selected_items()
            paths=[]
            # Prep each item for move/copy
            for item in items:
                itemNo=item[0]
                itemName=self.app.iconView.store[itemNo][COL_PATH]            
    
                nodeRef=self.app.iconView.store[itemNo][COL_NODEREF]
                # Repo to repo copy/move            
                if target_id==0:
                    if self.app.currentDirectory=="/":
                        uri="cmis:///"+itemName
                    else:
                        uri="cmis://"+self.app.currentDirectory+"/"+itemName                
                else:
                    # repo to local copy
                    if context.action ==0:                        
                        localPath=unicode(self.getLocalItemPath(self.app.currentDirectory,itemName))                        
                        uri="file://"+localPath
                        
                    else:                        
                        self.app.util.statusMessage("Downloading "+itemName+" ...")
                        localPath=unicode(self.copyLocalRecursive(self.app.currentDirectory,itemName))
                        self.app.util.statusMessage("Downloading "+itemName+" ... done.")
                        uri="file://"+localPath
                        self.newDrag=False
                        
                paths.append(uri)
    
            if target_id==0:
                data=""
                for path in paths:
                    data=data+path+"\r\n"
    
                selection.set("text/uri-list",8,data)
            else:
                res=selection.set_uris(paths)
            self.selectionPaths=paths                
            return True
        else:
            if target_id==0:
                data=""
                for path in self.selectionPaths:
                    data=data+path+"\r\n"
    
                selection.set("text/uri-list",8,data)
            else:
                res=selection.set_uris(self.selectionPaths)            
    
    def onDragEnd(self,widget,context):
        """
        Called when D&D is over
        Refresh the iconView if it was a move (so the source changed because the moved item(s) disappear
        """        
        if context.action == gtk.gdk.ACTION_MOVE:
                        
            self.app.iconView.fillStore()
    
    def onDragBegin(self,widget,context):
        """
        Called when D&D begins
        """            
        print ("*** DRAG BEGIN ***")
        self.newDrag=True
    
    
    def onDragDataDelete(self,widget,context,data):
        """
        Called when it's safe to remove data from the source
        """        
        if context.action == gtk.gdk.ACTION_MOVE:
            self.app.iconView.fillStore()
    
 
    def copyLocalRecursive(self,path,itemName):
        """
        Creates a local copy of the given item
        """        
        if path=="/":
            itemPath="/"+itemName
        else:
            itemPath=path+"/"+itemName                
        itemPath=path+"/"+itemName
        itemNode = self.app.repo.getObjectByPath(itemPath)
                    
        localItemPath=self.app.config.get("paths","local")+"/"+self.app.repo.id+itemPath
        localDirPath=os.path.dirname(localItemPath)
        
        if os.path.exists(localDirPath)==False:
            os.makedirs(localDirPath)
        #if os.path.exists(localFilePath):
            #os.chmod(localFilePath, stat.S_IREAD + stat.S_IWRITE)
        # If we are working on a file, get the contents across
        if itemNode.getProperties()["cmis:baseTypeId"]=="cmis:document":            
            o = open(localItemPath, 'wb')
            result = itemNode.getContentStream()
            o.write(result.read())
            result.close()
            o.close()
        else: 
            # If we are working on a folder, create it and get the contents
            if os.path.exists(localItemPath)==False:
                os.makedirs(localItemPath)
            children=itemNode.getChildren()
            for child in children:
                self.copyLocalRecursive(itemPath,child.name)

        return localItemPath
    
    def getLocalItemPath(self,path,itemName):
        """
        Gets path of local copy to file
        """
        if path=="/":
            itemPath="/"+itemName
        else:
            itemPath=path+"/"+itemName                
        itemPath=path+"/"+itemName
        itemNode = self.app.repo.getObjectByPath(itemPath)
                    
        localItemPath=self.app.config.get("paths","local")+"/"+self.app.repo.id+itemPath
        return localItemPath
