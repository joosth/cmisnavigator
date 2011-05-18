#!/usr/bin/python
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
CMIS Navigator
**************
"""
import gtk
import gobject
import os
import urllib
import urllib2
import gtk.glade
import platform
import gtk.gdk
import stat
import ConfigParser, os
import subprocess

from cmislib.model import CmisClient, Repository, Folder
from contextmenu import ContextMenu
from menubar import MenuBar
from dragdrop import DragDrop
from util import Util
from toolbar import ToolBar
from iconview import IconView

from constants import *


class PyApp(gtk.Window):
    """
    Main navigator application
    """
    
    
    iconView=None
    def __init__(self):
        super(PyApp, self).__init__()
        self.util=Util(self)
        
        # Start in browse mode
        self.viewType=VIEW_BROWSE
        
        # Get the application icon
        self.set_icon_from_file("theme/apps/navigator.png")
        
        #Read config from navigator.cfg and .navigator.cfg 
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open('navigator.cfg'))
        self.config.read(['navigator.cfg', os.path.expanduser('~/.navigator.cfg')])

        #Get dialogs 
        self.gladefile = "navigator.glade"  
        self.wTree = gtk.glade.XML(self.gladefile)         
        self.wTree.signal_autoconnect(self)        
        
        self.statusbar=gtk.Statusbar()
        
        self.set_size_request(650, 400)
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.connect("destroy", gtk.main_quit)
        self.set_title("CMIS Navigator")
                
        # Init CMIS client and get root folder
        cmisClient = CmisClient(self.config.get('cmis','url'), self.config.get('cmis','username'), self.config.get('cmis','password'))
        
        self.repo = cmisClient.defaultRepository
        
        self.rootFolder = self.repo.rootFolder
        self.rootDirectory=self.config.get('navigator','root')
        self.currentDirectory = self.rootDirectory

        vbox = gtk.VBox(False, 0);
        
        menubar = MenuBar(self)        
        vbox.pack_start(menubar.menuBar, False, False, 0)

        self.toolbar=ToolBar(self) 
        vbox.pack_start(self.toolbar.toolbar, False, False, 0)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw, True, True, 0)
        
        # The icon viewer
        self.iconView=IconView(self)
        sw.add(self.iconView.widget)
        self.iconView.widget.grab_focus()
        
        # Add D&D functionality
        self.dragdrop=DragDrop(self)
        
               
        vbox.pack_start(self.statusbar, False, False, 0)

        self.add(vbox)

        self.statusbar.push(1,"Repository: "+self.repo.id);        
        self.show_all()
    
PyApp()
gtk.main()
