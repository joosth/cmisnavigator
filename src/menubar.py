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
Menu bar
********
Provides the menu bar for the Navigator
"""

import gtk
from util import *
import os
class MenuBar():
    """
    The menu bar for the navigator
    """    
    def __init__(self,app):
        
        self.app=app
        self.menuBar = gtk.MenuBar()
        
        # File menu
        fileMenu = gtk.Menu()
        
        fileMenuItem = gtk.MenuItem("File")
        self.menuBar.append(fileMenuItem)        

                        
        
        newFileItem=gtk.MenuItem("New file...")
        fileMenu.append(newFileItem)        
        newFileItem.connect('button_press_event', self.onNewFileClicked)
        
        newFolderItem=gtk.MenuItem("New folder...")
        fileMenu.append(newFolderItem)
        newFolderItem.connect('button_press_event', self.onNewFolderClicked)
                
        fileMenuItem.set_submenu(fileMenu)
        
        # Help menu        
        helpMenu = gtk.Menu()
                        
        helpMenuItem = gtk.MenuItem("Help")        
        self.menuBar.append(helpMenuItem)
        
        aboutItem=gtk.MenuItem("About CMIS Navigator")
        helpMenu.append(aboutItem)
        aboutItem.connect('button_press_event', self.onAboutClicked)

        helpMenuItem.set_submenu(helpMenu)
                
        self.menuBar.show_all()

    def onAboutClicked(self,event,item):
        """
        Show the about dialog
        """
        
        self.aboutDialog = self.app.wTree.get_widget("aboutDialog")        
        self.aboutDialog.show()        
        self.aboutDialog.run()        
        self.aboutDialog.hide()
    
    def onNewFileClicked(self,event,item):
        """
        Show new file dialog
        """
        newFileDialog = self.app.wTree.get_widget("newFileDialog")                
        newFileDialog.show()        
        response=newFileDialog.run()        
        newFileDialog.hide()
        if response==1:
            filePaths = newFileDialog.get_filenames()
            folder = self.app.repo.getObjectByPath(self.app.currentDirectory)
            for filePath in filePaths:                
                if not os.path.isdir(filePath):
                    f=open(filePath,"rb")
                    fnameparts=filePath.split("/")
                    fileName=fnameparts[len(fnameparts)-1]
                    self.app.statusbar.push(1,"Creating file "+fileName+ " ...");
                    while gtk.events_pending():
                        gtk.main_iteration()
                    try:        
                        folder.createDocument(fileName,{},f)
                    except:
                        self.app.util.errorMessage("uploading file failed! ")
                    self.app.statusbar.push(1,"Creating file "+fileName+ " ... done");
                    while gtk.events_pending():
                        gtk.main_iteration()   
            self.app.iconView.fillStore()
        
    def onNewFolderClicked(self,event,item):
        """
        Show new folder dialog
        """
        self.newFolderDialog = self.app.wTree.get_widget("newFolderDialog")
                
        self.newFolderDialog.show()        
        response=self.newFolderDialog.run()        
        self.newFolderDialog.hide()
        if response==1:
            folderName=self.app.wTree.get_widget("folderName").get_text()
            if folderName!=None and len(folderName)>0:
           
                self.app.statusbar.push(1,"Creating folder "+folderName+ " ...");
                while gtk.events_pending():
                    gtk.main_iteration()
                folder = self.app.repo.getObjectByPath(self.app.currentDirectory)
        
                folder.createFolder(folderName,{})
                self.app.iconView.fillStore()
                self.app.statusbar.push(1,"Creating folder "+folderName+ " ... done.");
            else:
                self.app.util.errorMessage("Folder name cannot be empty")
        
    