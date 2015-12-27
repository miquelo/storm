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
from storm.module import util

import os.path

class Layout:

	"""
	Layout.
	"""
	
	def __init__(self):
	
		self.__executions = []
		
	@property
	def executions(self):
	
		"""
		List of :class:`ContainerExecution` values.
		"""
		
		return self.__executions
		
class Container:

	"""
	Container.
	
	:param storm.engine.image.ImageRef image_ref:
	   Container image reference.
	"""
	
	def __init__(self, image_ref):
	
		self.__image_ref = image_ref
		self.__ports = []
		
	@property
	def image_ref(self):
	
		"""
		Image reference.
		"""
		
		return self.__image_ref
		
	@property
	def ports(self):
	
		"""
		List of :class:`ContainerPort` values.
		"""
		
		return self.__ports
		
class ContainerPort:

	"""
	Port of container service.
	
	:param int value:
	   Port value.
	:param string service_name:
	   Service name.
	"""
	
	def __init__(self, value, service_name):
	
		self.__value = value
		self.__service_name = service_name
		
	@property
	def value(self):
	
		"""
		Port value.
		"""
		
		return self.__value
		
	@property
	def service_name():
	
		"""
		Service name.
		"""
		
		return self.__service_name
		
class ContainerExecution:
	
	"""
	Container execution for a platform.
	
	:param Container cont:
	   Container involved in this setup process.
	:param string plat_name:
	   Name of the target platform.
	:param ContainerExecutionConfig config:
	   Setup configuration.
	"""
	
	def __init__(self, cont, plat_name, config):
	
		self.__container = cont
		self.__platform_name = plat_name
		self.__configuration = config
		
	@property
	def container(self):
	
		"""
		Involved container.
		"""
		
		return self.__container
		
	@property
	def platform_name(self):
	
		"""
		Target platform name.
		"""
		
		return self.__platform_name
		
	@property
	def configuration(self):
	
		"""
		Setup configuration.
		"""
		
		return self.__configuration
		
class ContainerExecutionConfig:

	"""
	Container execution configuration.
	"""
	
	def __init__(self):
	
		self.__volumes = []
		
	@property
	def volumes(self):
	
		"""
		List of :class:`VolumeMount` values.
		"""
		
		return self.__volumes
		
class Volume:

	"""
	Volume.
	
	:param string stor_type:
	   Storage type.
	:param int size:
	   Available size.
	"""
	
	def __init__(self, stor_type, size):
	
		self.__storage_type = stor_type
		self.__size = size
		
	@property
	def storage_type(self):
	
		"""
		Storage type.
		"""
		
		return self.__storage_type
		
	@property
	def size(self):
	
		"""
		Available size.
		"""
		
		return self.__size
		
class VolumeMount:

	"""
	Volume mount inside a container.
	
	:param Volume volume:
	   Volume to mount.
	:param string path:
	   Mount path inside container.
	"""
	
	def __init__(self, volume, path):
	
		self.__volume = volume
		self.__path = path
		
	@property
	def volume(self):
	
		"""
		Volume to mount.
		"""
		
		return self.__volume
		
	@property
	def path(self):
	
		"""
		Mount path.
		"""
		
		return self.__path
		
def load(layout_data, props=None):

	"""
	Load a layout from the given data dictionary.
	
	:param dict layout_data:
	   Dictionary with layout data.
	:param props:
	   Optional properties.
	:rtype:
	   Layout
	:return:
	   The loaded layout.
	   
	An example:
	
	.. code-block:: json
	
		{
		    "containers" : {
		        "members-service-01": {
		            "image": {
		                "name": "members-service",
		                "version": "2.3"
		            },
		            "ports": [
		                {
		                    "value": "80",
		                    "service": "members"
		                }
		            ]
		        }
		    },
		    "volumes": {
		        "members-volume-01": {
		            "storage": "local",
		            "size": "8Gb"
		        }
		    },
		    "executions": [
		        {
		            "container": "members-service-01",
		            "platform": "local",
		            "configuration": {
		                "volumes": {
		                    "volume": "members-volume-01",
		                    "path": "/var/database"
		                }
		            }
		        }
		    ]
		}
		
	It may have resolvable fragments.
	"""

