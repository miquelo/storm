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

from storm import image
from storm import layout
from storm import printer
from storm import util

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
		self.__layouts = {}
		self.__printer_fact = printer.PrinterFactory()
		
		try:
			config_file = self.__config_file_open("r")
			config = json.loads(config_file.read())
			
			if "platforms" in config:
				for plat_name, plat_data in config["platforms"].items():
					self.__platforms[plat_name] = {
						"provider": plat_data["provider"],
						"config": plat_data["config"]
					}
					
			if "layouts" in config:
				for lay_name, lay_data in config["layouts"].items():
					self.__layouts[lay_name] = {
						"directory": lay_data["directory"],
						"config": lay_data["config"]
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
		
	def __layout_load(self, name):
	
		try:
			lay_data = self.__layouts[name]
		except KeyError:
			raise Exception("Layout '{}' does not exist".format(name))
		try:
			lay_dir = lay_data["directory"]
		except KeyError:
			raise Exception("Layout directory is not defined")
		if not os.path.exists(lay_dir):
			raise Exception("Layout directory does not exist")
		try:
			config = lay_data["config"]
		except KeyError:
			config = {}
			
		return layout.Layout(lay_dir, config)
		
	def __images_load(self, source_dir, config=None):
	
		images_path = os.path.join(source_dir, "storm-images.json")
		images = json.loads(open(images_path, "r").read())
		
		props = {}
		if "properties" in images:
			util.merge_dict(props, images["properties"])
		if config is not None:
			util.merge_dict(props, config)
		props = util.resolvable_dict(props, props)
		
		if "images" in images:
			for image_data in images["images"]:
				image_def = util.resolvable_dict(image_data, props)
				ref = self.__image_ref(image_def)
				if "extends" in image_def:
					extends = self.__image_ref(image_def["extends"])
				else:
					extends = None
				definition = image_def["definition"]
				yield image.Image(name, ref, extends, definition)
				
	def __image_ref(self, ref_def):
	
		name = ref_def["name"]
		if "version" in ref_def:
			version = ref_def["version"]
		else:
			version = None
		return image.ImageRef(name, version)
		
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
		
	def layouts(self):
	
		return self.__layouts
		
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
		
	def offer(self, name, source_dir, config):
	
		plat = self.__platform_load(name)
		for image in self.__images_load(source_dir, config):
			plat.build(image)
			plat.publish(image)
		
	def retire(self, name, source_dir):
	
		plat = self.__platform_load(name)
		for image in self.__images_load(source_dir):
			plat.delete(image)
		
	def bind(self, layout_name, bound_dir, config):
	
		self.__layouts[layout_name] = {
			"directory": bound_dir,
			"config": config
		}
		
	def leave(self, name, destroy):
	
		lay = self.__layout_load(name)
		if destroy:
			lay.destroy()
		del self.__layouts[name]
		
	def store(self):
	
		config = {
			"platforms": {},
			"layouts": {}
		}
		for plat_name, plat_data in self.__platforms.items():
			config["platforms"][plat_name] = plat_data
		for lay_name, lay_data in self.__layouts.items():
			config["layouts"][lay_name] = lay_data
			
		config_file = self.__config_file_open("w")
		config_file.write(json.dumps(config, sort_keys=True, indent=4))
		config_file.write("\n")
		config_file.close()

