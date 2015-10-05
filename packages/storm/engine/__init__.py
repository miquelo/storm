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

from storm.engine import image
from storm.engine import layout
from storm.engine import printer

from storm.module import jsons
from storm.module import resource
from storm.module import util

import importlib

#
# Engine
#
class Engine:

	def __init__(self, config_res):
	
		self.__config_res = config_res
		self.__platforms = {}
		self.__layouts = {}
		self.__printer_fact = printer.PrinterFactory()
		
		try:
			config_file = self.__config_res.open("r")
			config_in = jsons.read(config_file)
			if config_in is None:
				config = {}
			else:
				config = config_in.value()
			
			if "platforms" in config:
				for plat_name, plat_data in config["platforms"].items():
					self.__platforms[plat_name] = {
						"provider": plat_data["provider"],
						"properties": plat_data["properties"]
					}
			if "layouts" in config:
				for lay_name, lay_data in config["layouts"].items():
					self.__layouts[lay_name] = {
						"resource": lay_data["resource"],
						"properties": lay_data["properties"]
					}
		except resource.ResourceNotFoundError:
			pass
		
	def __platform_res(self, name):
	
		platforms_res = self.__config_res.parent().ref("platforms")
		return platforms_res.ref(name)
		
	def __platform_inst(self, name, prov):
	
		try:
			p_mod_name = "storm.provider.platform.{}".format(prov)
			p_mod = importlib.import_module(p_mod_name)
			return p_mod.Platform(
				self.__platform_res(name),
				self.__printer_fact.printer
			)
		except BaseException:
			err_msg = "Could not instantiate platform of with provider '{}'"
			raise Exception(err_msg.format(prov))
			
	def __platform_load(self, name):
	
		try:
			plat_data = self.__platforms[name]
		except KeyError:
			raise Exception("Platform '{}' does not exist".format(name))
			
		plat = self.__platform_inst(name, plat_data["provider"])
		plat.load(plat_data["properties"])
		
		return plat
		
	def __layout_load(self, name):
	
		try:
			layout_data = self.__layouts[name]
		except KeyError:
			msg = "Layout '{}' is not bound".format(name)
			raise Exception(msg)
			
		try:
			layout_res = resource.ref(layout_data["resource"])
		except KeyError:
			msg = "Layout '{}' resource is not defined".format(name)
			raise Exception(msg)
			
		layout_file = layout_res.open("r")
		layout_config = json.loads(layout_file.read())
		layout_file.close()
		
		layout_props = {}
		if "properties" in layout_config:
			util.merge_dict(layout_props, layout_config["properties"])
		if "properties" in layout_data:
			util.merge_dict(layout_props, layout_data["properties"])
			
		layout_data = util.resolvable(layout_config["layout"], layout_props)
		return layout.Layout(layout_res.parent(), layout_data)
		
	def __image_load(self, image_res, props=None):
	
		image_file = image_res.open("r")
		image_config = json.loads(image_file.read())
		image_file.close()
		
		image_props = {}
		if "properties" in image_config:
			util.merge_dict(image_props, image_config["properties"])
		if props is not None:
			util.merge_dict(image_props, props)
			
		image_data = util.resolvable(image_config["image"], image_props)
		return image.Image(image_res.parent(), image_data)
		
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
		
	def register(self, name, prov, props):
	
		if name in self.__platforms:
			raise Exception("Platform '{}' already exists".format(name))
		
		plat = self.__platform_inst(name, prov)
		plat.configure(props)
		
		self.__platforms[name] = {
			"provider": prov,
			"properties": plat.save()
		}
		
	def dismiss(self, name, destroy):
	
		plat = self.__platform_load(name)
		if destroy:
			plat.destroy()
			self.__platform_res(name).delete()
		del self.__platforms[name]
		
	def offer(self, name, image_res, props):
	
		plat = self.__platform_load(name)
		image = self.__image_load(image_res, props)
		plat.build(image)
		plat.publish(image)
		
	def retire(self, name, image_res):
	
		plat = self.__platform_load(name)
		image = self.__image_load(image_res)
		plat.delete(image)
		
	def bind(self, layout_name, layout_res, props):
	
		if layout_name in self.__layouts:
			msg = "Layout '{}' already bound".format(layout_name)
			raise Exception(msg)
		self.__layouts[layout_name] = {
			"resource": layout_res.unref(),
			"properties": props
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
			
		config_file = self.__config_res.open("w")
		jsons.write_dict(config_file, config)
		config_file.write("\n")
		config_file.close()

