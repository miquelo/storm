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

class Container:

	def __init__(self, config):
	
		self.__image = config["image"]
		self.__version = config["version"]
		
		self.__ports = {}
		if "ports" in config:
			for port_name, port_value in config["ports"].items():
				self.__ports[port_name] = port_value
				
		self.__platform = {}
		if "platform" in config:
			for plat_name, plat_reg in config["platform"].items():
				self.__platform[plat_name] = plat_reg

