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

from storm import util
from storm.layout import container

import json
import os.path

class Layout:

	def __init__(self, bound_dir, config):
	
		layout_path = os.path.join(bound_dir, "storm-layout.json")
		layout_config = json.loads(open(layout_path, "r").read())
		util.merge_dict(layout_config, config)
		
		self.__containers = []
		if "containers" in layout_config:
			for cont_config in layout_config["containers"]:
				self.__containers.append(container.Container(cont_config))
				
	def destroy(self):
	
		pass

