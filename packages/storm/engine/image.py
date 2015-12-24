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
from storm.module import resource

import os.path

class Image:

	"""
	Container image.
	
	:param storm.engine.image.ImageRef ref:
	   Image reference.
	:param storm.engine.image.ImageRef extends:
	   Extended image reference, if any.
	"""
	
	class __ImageResource:
	
		def __init__(self, source_res, target_res, props):
		
			self.__source_res = source_res
			self.__target_res = target_res
			self.__properties = props
			
		@property
		def source_res(self):
		
			return self.__source_res  
			
		@property
		def target_res(self):
		
			return self.__target_res
			
		@property
		def properties(self):
		
			return self.__properties
			
	class __ImageCommand:
	
		def __init__(self, args):
		
			self.__arguments = args
				
		@property
		def arguments(self):
		
			return self.__arguments
			
	def __init__(self, ref, extends=None):
		
		self.__ref = ref
		self.__extends = extends
		self.__resources = []
		self.__provision = []
		self.__execution = []
		
	@property
	def ref(self):
	
		return self.__ref
		
	@property
	def extends(self):
	
		return self.__extends
		
	@property
	def resources(self):
	
		return self.__resources
		
	@property
	def provision(self):
	
		return self.__provision
		
	@property
	def execution(self):
	
		return self.__execution
		
	def resources_add(self, source_res, target_path, props):
	
		self.__resources.append(self.__ImageResource(
			source_res,
			resource.ref("image:///").ref(target_path),
			props
		))
		
	def provision_add(self, args):
	
		self.__provision.append(self.__ImageCommand(args))
		
	def execution_add(self, args):
	
		self.__execution.append(self.__ImageCommand(args))
		
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
		
def load(image_res):

	# data_file = data_res.open("r")
	# data = jsons.read(data_file).value()
	# data_file.close()
	# 
	# image_props = {}
	# if "properties" in data:
	# 	util.merge_dict(image_props, data["properties"])
	# util.merge_dict(image_props, props)
	# image_data = util.resolvable(data["image"], image_props)
	# 
	# self.__ref = ImageRef(image_data)
	# if "extends" in image_data:
	# 	self.__extends = ImageRef(image_data["extends"])
	# else:
	# 	self.__extends = None
	# 	
	# definition = image_data["definition"]
	# self.__definition = ImageDef(data_res.parent(), definition)
	
	pass

