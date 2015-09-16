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

class Image:

	def __init__(self, image_data):
	
		self.__ref = ImageRef(image_data)
		if "extends" in image_data:
			self.__extends = ImageRef(image_data["extends"])
		else:
			self.__extends = None
		self.__definition = ImageDef(image_data["definition"])
		
	@property
	def ref(self):
	
		return self.__ref
		
	@property
	def extends(self):
	
		return self.__extends
		
	@property
	def definition(self):
	
		return self.__definition
		
class ImageRef:

	def __init__(self, ref_data):
	
		self.__name = ref_data["name"]
		if "version" in ref_data:
			self.__version = ref_data["version"]
		else:
			self.__version = None
			
	@property
	def name(self):
	
		return self.__name
		
	@property
	def version(self):
	
		return self.__version
		
class ImageDef:

	def __init__(self, def_data):
	
		self.__files = []
		if "files" in def_data:
			for file_data in def_data["files"]:
				self.__files.append(ImageFile(file_data))
		self.__provision = []
		if "provision" in def_data:
			for prov_data in def_data["provision"]:
				self.__provision.append(ImageCommand(prov_data))
		self.__execution = []
		if "execution" in def_data:
			for exec_data in def_data["execution"]:
				self.__execution.append(ImageCommand(exec_data))
				
	@property
	def files(self):
	
		return self.__files
		
	@property
	def provision(self):
	
		return self.__probision
		
	@property
	def execution(self):
	
		return self.__execution
		
class ImageFile:

	def __init__(self, file_data):
	
		self.__source = file_data["source"]
		if "target" in file_data:
			self.__target = file_data["target"]
		else:
			self.__target = self.__source
			
	@property
	def source(self):
	
		return self.__source
		
	@property
	def target(self):
	
		return self.__target
		
class ImageCommand:

	def __init__(self, cmd_data):
	
		self.__args = []
		for arg in cmd_data:
			self.__args.append(arg)
			
	@property
	def args(self):
	
		return self.__args
