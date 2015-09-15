#
# This file is part of STORM.
#
# STORM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# STORM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STORM.  If not, see <http://www.gnu.org/licenses/>.
#

class ImageRef:

	def __init__(self, name, version):
	
		self.__name = name
		self.__version = version
		
	@property
	def name(self):
	
		return self.__name
		
	@property
	def version(self):
	
		return self.__version
		
class Image:

	def __init__(self, ref, extends, definition):
	
		self.__ref = ref
		self.__extends = extends
		self.__definition = definition
		
	@property
	def ref(self):
	
		return self.__ref
		
	@property
	def extends(self):
	
		return self.__extends
		
	@property
	def definition(self):
	
		return self.__definition

