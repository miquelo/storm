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

from storm.engine import container

from storm.module import jsons
from storm.module import util

import os.path

class Layout:

	def __init__(self, data_res, props):
		
		data_file = data_res.open("r")
		data = jsons.read(data_file).value()
		data_file.close()
		
		layout_props = {}
		if "properties" in data:
			util.merge_dict(layout_props, data["properties"])
		util.merge_dict(layout_props, props)
		layout_data = util.resolvable(data["layout"], layout_props)
		
		self.__data_res = data_res
		self.__props = props
		self.__containers = []
		
		#	if "containers" in layout_data:
		#		for cont_data in layout_data["containers"]:
		#			self.__containers.append(container.Container(cont_data))
		
	def unref(self):
	
		return self.__data_res.unref()
		
	def properties(self):
	
		return self.__props
		
	def destroy(self):
	
		pass

