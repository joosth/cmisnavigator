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
# Created on May 12, 2011
# Joost Horward


"""
Constants
*********
"""

#: Path column
COL_PATH = 0
#: Column for icon
COL_PIXBUF = 1
#: Column number that holds boolean (true if item is a directory)
COL_IS_DIRECTORY = 2
#: Column number that holds the tooltip string
COL_TOOLTIP=3
#: Column number that holds the NodeRef
COL_NODEREF=4
#: Column number that holds the checked out flag 
COL_IS_CHECKED_OUT=5

"""
Constants that determine what we see in the icon view

"""
#: View mode is Browse (normal view of a folder)
VIEW_BROWSE=0
#: View mode is PWC (working copies)
VIEW_PWC=1
#: View mode is search results
VIEW_SEARCHRESULT=2