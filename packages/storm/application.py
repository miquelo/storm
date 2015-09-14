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

from storm import printer

import importlib
import json
import os
import shutil

#
# Application
#
class Application:

	def __init__(self, data_dir):
	
		self.__data_dir = data_dir
		self.__platforms = {}
		self.__printer_fact = printer.PrinterFactory()
		
		try:
			config_file = self.__config_file_open("r")
			config = json.loads(config_file.read())
			for plat_name, plat_data in config["platforms"].items():
				self.__platforms[plat_name] = {
					"provider": plat_data["provider"],
					"config": plat_data["config"]
				}
			config_file.close()
		except FileNotFoundError:
			pass
		
	def __config_file_open(self, oflags):
	
		return open(os.path.join(self.__data_dir, "config.json"), oflags)
		
	def __platform_dir(self, name):
	
		platforms_dir = os.path.join(self.__data_dir, "platforms")
		platform_dir = os.path.join(platforms_dir, name)
		if not os.path.exists(platform_dir):
			os.makedirs(platform_dir)
		return platform_dir
		
	def __platform_inst(self, name, class_name):
	
		try:
			p_mod_name, sep, p_class_name = class_name.rpartition(".")
			p_mod = importlib.import_module(p_mod_name)
			return getattr(p_mod, p_class_name)(
				self.__platform_dir(name),
				self.__printer_fact.printer
			)
		except BaseException:
			err_msg = "Could not instantiate platform of with provider '{}'"
			raise Exception(err_msg.format(class_name))
			
	def __platform_load(self, name):
	
		try:
			plat_data = self.__platforms[name]
		except KeyError:
			raise Exception("Platform '{}' does not exist".format(name))
			
		plat = self.__platform_inst(name, plat_data["provider"])
		plat.load(plat_data["config"])
		
		return plat
		
	@property
	def printer_level(self):
	
		return self.__printer_fact.level
		
	@printer_level.setter
	def printer_level(self, value):
	
		self.__printer_fact.level = value
		
	def printer(self, out):
	
		return self.__printer_fact.printer(out)
		
	def platforms(self):
	
		return self.__platforms
		
	def register(self, name, prov, config):
	
		if name in self.__platforms:
			raise Exception("Platform '{}' already exists".format(name))
		
		plat = self.__platform_inst(name, prov)
		plat.configure(config)
		
		self.__platforms[name] = {
			"provider": prov,
			"config": plat.save()
		}
		
	def dismiss(self, name, destroy):
	
		plat = self.__platform_load(name)
		if destroy:
			plat.destroy()
			shutil.rmtree(self.__platform_dir(name))
		del self.__platforms[name]
		
	def offer(self, name, image_name, source_dir, config):
	
		plat = self.__platform_load(name)
		
		image_def = None # Retrieve from source_dir
		plat.build(image_name, image_def, config)
		plat.publish(image_name, image_def, config)
		
	def retire(self, name, image_name):
	
		plat = self.__platform_load(name)
		plat.delete(image_name)
		
	def store(self):
	
		config = {
			"platforms": {}
		}
		for plat_name, plat_data in self.__platforms.items():
			config["platforms"][plat_name] = plat_data
			
		config_file = self.__config_file_open("w")
		config_file.write(json.dumps(config, sort_keys=True, indent=4))
		config_file.write("\n")
		config_file.close()

