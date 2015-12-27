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
from storm.module import util

import os.path

class Image:

	"""
	Container image.
	
	:param ImageRef ref:
	   Image reference.
	:param ImageRef extends:
	   Extended image reference, if any.
	"""
			
	def __init__(self, ref, extends=None):
		
		self.__ref = ref
		self.__extends = extends
		self.__ports = []
		self.__resources = []
		self.__provision = []
		self.__execution = []
		
	@property
	def ref(self):
	
		"""
		Image reference of type :class:`ImageRef`.
		"""
		
		return self.__ref
		
	@property
	def extends(self):
	
		"""
		Extended image reference of type :class:`ImageRef`.
		"""
		
		return self.__extends
		
	@property
	def ports(self):
	
		"""
		List of :class:`ImagePort` values to be exposed.
		"""
		
		return self.__ports
		
	@property
	def resources(self):
	
		"""
		List of :class:`ImageResource` values.
		"""
		
		return self.__resources
		
	@property
	def provision(self):
	
		"""
		List of :class:`ImageCommand` values for provisioning.
		"""
		
		return self.__provision
		
	@property
	def execution(self):
	
		"""
		List of :class:`ImageCommand` values for execution.
		"""
		
		return self.__execution
		
class ImageRef:

	"""
	Container image reference.
	
	:param string name:
	   Image name.
	:param string version:
	   Image version.
	"""
	
	def __init__(self, name, version=None):
	
		self.__name = name
		self.__version = version
		
	@property
	def name(self):
	
		"""
		Image name.
		"""
		
		return self.__name
		
	@property
	def version(self):
	
		"""
		Image version.
		"""
		
		return self.__version
		
class ImagePort:

	"""
	Port exposed by an image.
	
	:param string name:
	   Port name.
	:param int value:
	   Port value.
	:param string proto:
	   Tranport protocol. By default it is "tcp".
	"""
	
	def __init__(self, name, value, proto=None):
	
		self.__name = name
		self.__value = value
		self.__protocol = proto
		
	@property
	def name(self):
	
		"""
		Port name.
		"""
		
		return self.__name
		
	@property
	def value(self):
	
		"""
		Port value.
		"""
		
		return self.__value
		
	@property
	def protocol(self):
	
		"""
		Transport protocol.
		"""
		
		return self.__value
		
class ImageResource:

	"""
	Container image resource with the given source resource, target path and
	properties.
	
	:param Resource source_res:
	   Source resource.
	:param string target_path:
	   Target path.
	:param props:
	   Optional properties.
	"""
	
	def __init__(self, source_res, target_path, props=None):
	
		self.__source_res = source_res
		self.__target_path = target_path
		self.__properties = props
		
	@property
	def source_res(self):
	
		"""
		Source resource.
		"""
		
		return self.__source_res  
		
	@property
	def target_path(self):
	
		"""
		Target path.
		"""
		
		return self.__target_path
		
	@property
	def properties(self):
	
		"""
		Optional properties.
		"""
		
		return self.__properties
		
class ImageCommand:

	"""
	Container image command with the given resources.
	
	:param list args:
	   Command arguments.
	"""
	
	def __init__(self, args):
	
		self.__arguments = args
		
	@property
	def arguments(self):
	
		"""
		Command arguments.
		"""
		
		return self.__arguments
		
def load(base_res, image_data, props=None):

	"""
	Load a container image from the given data dictionary.
	
	:param Resource base_res:
	   Base resource.
	:param dict image_data:
	   Dictionary with image data.
	:param props:
	   Optional properties.
	:rtype:
	   Image
	:return:
	   The loaded image.
	   
	An example:
	
	.. code-block:: json
	
	   {
	       "properties": {
	       },
	       "image": {
	           "name": "members-service",
	           "version": "2.3",
	           "extends": {
	               "name": "rest-service",
	               "version": "1.4"
	           },
	           "ports": [
	               {
	                   "name": "http",
	                   "value": 80
	               }
	           ],
	           "resources": [
	               {
	                   "source": {
	                       "uri": ""
	                   },
	                   "target": "",
	                   "properties": {
	                   }
	               },
	               {
	                   "source": {
	                       "uri": "",
	                       "properties": {
	                       }
	                   },
	                   "target": "",
	                   "properties": {
	                   }
	               }
	           ],
	           "provision": [
	               {
	                   "arguments": []
	               }
	           ],
	           "execution": [
	               {
	                   "arguments": []
	               }
	           ]
	       }
	   }
	   
	Data dictionary will be treated as a resolvable one.
	"""
	
	def load_ref(data):
	
		version = data["version"] if "version" in data else None
		return ImageRef(data["name"], version)
		
	image_props = {}
	if "properties" in image_data:
		util.merge_dict(image_props, image_data["properties"])
	if props is not None:
		util.merge_dict(image_props, props)
	image_def = resolver.resolvable(image_data["image"], image_props)
	
	image_ref = load_ref(image_data)
	if "extends" in image_def:
		image_extends = load_ref(image_def["extends"])
	else:
		image_extends = None
	image = Image(image_ref, image_extends)
	
	if "resources" in image_def:
		for res in image_def["resources"]:
			res_source = res["source"]
			res_source_uri = res_source["uri"]
			try:
				if "properties" in res_source:
					res_source_props = res_source["properties"]
				else:
					res_source_props = None
				source_res = resource.ref(res_source_uri, res_source_props)
			except:
				source_res = base_res.ref(res_source_uri)
			res_target = res["target"]
			res_props = res["properties"] if "properties" in res else None
			image.resources.append(ImageResource(
				source_res,
				res_target,
				res_props
			))
			
	if "provision" in image_def:
		for prov in image_def["provision"]:
			image.provision.append(ImageCommand(prov))
			
	if "execution" in image_def:
		for execut in image_def["execution"]:
			image.execution.append(ImageCommand(execut))

