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
from distutils.core import setup
import py2exe
import glob


#import modulefinder
#modulefinder.AddPackagePath("cmislib.model", "CmisClient")




setup(
    name = 'bozexplorer',
    description = 'BOZ Explorer',
    version = '1.0',

    windows = [
                  {
                      'script': 'bozexplorer.py',
              #
              #'icon_resources': [(1, "../theme/places/folder.png")],
                  }
              ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo,gtk,gtk.glade,urllib2,gobject,os,gio,pango,pangocairo,atk,gobject,pygtk,cmislib.model,platform'
                  }
              },

    data_files=[
                   ('',['bozexplorer.glade']),
                   ('theme/mimetypes', glob.glob('theme/mimetypes/*')),
                   ('theme/places', glob.glob('theme/places/*'))                   
               ]
)