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

from storm.module import resource

import os
import os.path
import shutil

class Directory:

	def __init__(self, path, flags):
	
		self.__path = path
		self.__flags = flags
		
	def change(self):
	
		old = Directory(os.getcwd(), self.__flags)
		os.chdir(self.__path)
		return old
		
	def close(self):
	
		pass
		
class ResourceHandler:

	def __init__(self, uri, props):
		
		if uri.location is not None:
			msg = "File resource cannot have an explicit location"
			raise TypeError(msg)

		self.__uri = uri
		self.__props = props
		
	def __open_file(self, path, flags):
	
		try:
			return open(path, flags)
		except FileNotFoundError as err:
			raise resource.ResourceNotFoundError(err)
		
	def __open_dir(self, path, flags):
	
		return Directory(path, flags)
		
	def name(self):
	
		return os.path.basename(self.__uri.path)
		
	def exists(self):
	
		return os.path.exists(self.__uri.path)
		
	def delete(self):
	
		if self.exists():
			shutil.rmtree(self.__uri.path)
			return True
			
		return False
		
	def open(self, flags):
	
		path = self.__uri.path
		
		if self.exists():
			if os.path.isdir(path):
				open_fn = self.__open_dir
			elif os.path.isfile(path):
				open_fn = self.__open_file
			else:
				raise TypeError("Unsupported file type")
		else:
			if path.endswith("/"):
				path_dir = path
				open_fn = self.__open_dir
			else:
				path_dir = dirname(path)
				open_fn = self.__open_file
				
			if not os.path.exists(path_dir):
				os.makedirs(path_dir)
				
		return open_fn(path, flags)
		
def abspath(path):

	return os.path.abspath(path)
	
def isabs(path):

	return os.path.isabs(path)
	
def dirname(path):

	return os.path.dirname(path)
	
def join(base_path, rel_path):

	return os.path.join(base_path, rel_path)

