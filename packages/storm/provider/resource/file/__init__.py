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
		
class ResourceHandler:

	def __init__(self, uri, props):
		
		if uri.location is not None:
			msg = "File resource cannot have an explicit location"
			raise TypeError(msg)

		self.__uri = uri
		self.__props = props
		
	def exists(self):
	
		return os.path.exists(self.__uri.path)
		
	def name(self):
	
		return os.path.basename(self.__uri.path)
		
	def delete(self):
	
		if self.exists():
			shutil.rmtree(self.__uri.path)
			return True
		return False
		
	def open(self, flags):
	
		try:
			path = self.__uri.path
			if self.exists():
				if not os.path.isfile(path):
					raise TypeError("Not a file: '{}'".format(path))
			else:
				if path.endswith("/"):
					raise TypeError("Invalid file path: '{}'".format(path))
				path_dir = dirname(path)
				if not os.path.exists(path_dir):
					os.makedirs(path_dir)	
			return open(path, flags)
		except FileNotFoundError as err:
			raise resource.ResourceNotFoundError(err)
		
def abspath(path):

	return os.path.abspath(path)
	
def isabs(path):

	return os.path.isabs(path)
	
def dirname(path):

	return os.path.dirname(path)
	
def join(base_path, rel_path):

	return os.path.join(base_path, rel_path)

