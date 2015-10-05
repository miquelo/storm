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

	def __platform_provider(plat):
	
		return "{}.{}".format(plat.__module__, plat.__class__.__name__)
		
	def __init__(self, state_res):
	
		self.__state_res = state_res
		self.__platforms = {}
		self.__layouts = {}
		self.__printer_fact = printer.PrinterFactory()
		
		try:
			state_file = self.__state_res.open("r")
			state_in = jsons.read(state_file)
			if state_in is None:
				state = {}
			else:
				state = state_in.value()
			state_file.close()
			
			if "platforms" in state:
				for name, data in state["platforms"].items():
					self.__platforms[name] = self.__platform_load(
						name,
						data["provider"],
						data["properties"]
					)
			if "layouts" in state:
				for name, data in state["layouts"].items():
					self.__layouts[name] = layout.Layout(
						resource.ref(data["resource"]),
						data["properties"]
					)
		except resource.ResourceNotFoundError:
			pass
			
	def __platform_load(self, name, prov, props):
	
		mod_name, sep, class_name = prov.rpartition(".")
		mod = importlib.import_module(mod_name)
		return mod[class_name](
			self.__state_res.parent().ref("platforms").ref(name),
			props,
			self.__printer_fact.printer
		)
		
	@property
	def printer_level(self):
	
		return self.__printer_fact.level
		
	@printer_level.setter
	def printer_level(self, value):
	
		self.__printer_fact.level = value
		
	def printer(self, out):
	
		return self.__printer_fact.printer(out)
		
	def platforms(self):
	
		return {
			name: __platform_provider(plat)
			for name, plat in self.__platforms.items()
		}
		
	def layouts(self):
	
		return {
			name: lay.unref()
			for name, lay in self.__layouts.items()
		}
		
	def register(self, name, prov, props=None):
	
		self.__platforms[name] = self.__platform_load(name, prov, props or {})
		
	def dismiss(self, name, destroy):
	
		if destroy:
			self.__platforms[name].destroy()
		del self.__platforms[name]
		
	def offer(self, name, image_res, props=None):
	
		plat = self.__platforms[name]
		image = image.Image(image_res, props or {})
		plat.build(image)
		plat.publish(image)
		
	def retire(self, name, image_res):
	
		plat = self.__platforms[name]
		image = image.Image(image_res, {})
		plat.delete(image)
		
	def bind(self, layout_name, layout_res, props=None):
	
		self.__layouts[layout_name] = layout.Layout(
			layout_res,
			props or {}
		)
		
	def leave(self, name, destroy):
	
		if destroy:
			self__layouts[name].destroy()
		del self.__layouts[name]
		
	def store(self):
	
		state = {
			"platforms": {},
			"layouts": {}
		}
		for name, plat in self.__platforms.items():
			state["platforms"][name] = {
				"provider": __platform_provider(plat),
				"properties": plat.properties()
			}
		for name, lay in self.__layouts.items():
			state["layouts"][name] = {
				"resource": lay.unref(),
				"properties": lay.properties()
			}
		state_file = self.__state_res.open("w")
		jsons.write_dict(state_file, state, True)
		state_file.write("\n")
		state_file.close()

