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
Toolbar
*******
Provides a toolbar for the IconView
"""

import gtk
import os
import platform
import stat
import subprocess
import urllib
from cmislib.model import *

class ToolBar():
    """
    Toolbar class
    """
    
    def __init__(self,app):    
        menu = gtk.Menu()
        self.app=app
        self.toolbar = gtk.Toolbar()
        
        
        self.upButton = gtk.ToolButton(gtk.STOCK_GO_UP);
        self.upButton.set_is_important(True)
        self.upButton.set_sensitive(False)
        self.upButton.connect("clicked", self.onUpButtonClicked)
        self.toolbar.insert(self.upButton, -1)

        homeButton = gtk.ToolButton(gtk.STOCK_HOME)
        homeButton.set_is_important(True)        
        self.toolbar.insert(homeButton, -1)
        
        checkedoutButton=gtk.ToolButton(gtk.STOCK_HARDDISK)
        checkedoutButton.set_is_important(True)
        checkedoutButton.set_label("Checked out documents")
        self.toolbar.insert(checkedoutButton, -1)
        checkedoutButton.connect("clicked", self.onCheckedoutButtonClicked)
        
        homeButton.connect("clicked", self.onHomeButtonClicked)
    
    def onHomeButtonClicked(self, widget):
        """
        Switch to home folder
        """
        self.app.viewType=0
        self.app.currentDirectory = self.app.rootDirectory
        self.app.iconView.fillStore()
        self.upButton.set_sensitive(False)
        
    def onCheckedoutButtonClicked(self, widget):
        """
        Switch to checked out documents view
        """
        self.app.currentDirectory = "CHECKEDOUT"
        self.app.viewType=1
        self.app.iconView.fillStore()
        self.upButton.set_sensitive(False)
    
    def onUpButtonClicked(self, widget):
        """
        One folder up
        """
        self.app.currentDirectory = os.path.dirname(self.app.currentDirectory)
        self.app.iconView.fillStore()
        sensitive = True
        if self.app.currentDirectory == self.app.rootDirectory: sensitive = False
        self.upButton.set_sensitive(sensitive)
    
    