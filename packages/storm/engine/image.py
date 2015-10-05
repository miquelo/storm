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

from storm.module import jsons

import os.path

class Image:

	def __init__(self, data_res, props):
	
		data_file = data_res.open("r")
		data = jsons.read(data_file).value()
		data_file.close()
		
		image_props = {}
		if "properties" in data:
			util.merge_dict(image_props, data["properties"])
		util.merge_dict(image_props, props)
		image_data = util.resolvable(data["image"], image_props)
		
		self.__ref = ImageRef(image_data)
		if "extends" in image_data:
			self.__extends = ImageRef(image_data["extends"])
		else:
			self.__extends = None
			
		definition = image_data["definition"]
		self.__definition = ImageDef(data_res.parent(), definition)
		
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

	def __init__(self, res_parent, def_data):
	
		self.__resources = []
		if "resources" in def_data:
			for res_data in def_data["resources"]:
				self.__resources.append(ImageResource(res_parent, res_data))
		self.__provision = []
		if "provision" in def_data:
			for prov_data in def_data["provision"]:
				self.__provision.append(ImageCommand(prov_data))
		self.__execution = []
		if "execution" in def_data:
			for exec_data in def_data["execution"]:
				self.__execution.append(ImageCommand(exec_data))
				
	@property
	def resources(self):
	
		return self.__resources
		
	@property
	def provision(self):
	
		return self.__provision
		
	@property
	def execution(self):
	
		return self.__execution
		
class ImageResource:

	def __init__(self, res_parent, res_data):
	
		# Only relative sources? => resource.ref(...) redessign
		self.__source_res = res_parent.ref(res_data["source"])
		self.__target = res_data["target"]
		if "properties" in res_data:
			self.__properties = res_data["properties"]
		else:
			self.__properties = {}
			
	@property
	def source_res(self):
	
		return self.__source_res  
		
	@property
	def target(self):
	
		return self.__target
		
	@property
	def properties(self):
	
		return self.__properties
		
class ImageCommand:

	def __init__(self, cmd_data):
	
		self.__args = []
		for arg in cmd_data:
			self.__args.append(arg)
			
	@property
	def args(self):
	
		return self.__args

