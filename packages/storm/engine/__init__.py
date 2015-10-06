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
	
	class PlatformProxies:
	
		class PlatformProxy:
		
			def __init__(self, prov, props, state_res, printer_fact):
		
				self.__inst = None
				self.__prov = prov
				self.__props = props or {}
				self.__state_res = state_res
				self.__printer_fact = printer_fact
			
			def get(self, name):
		
				if self.__inst is None:
					prov = self.__prov
					mod_name = "{}{}".format("storm.provider.platform.", prov)
					mod = importlib.import_module(mod_name)
					self.__inst = getattr(mod, "Platform")(
						self.__state_res.parent().ref("platforms").ref(name),
						self.__props,
						self.__printer_fact.printer
					)
				return self.__inst
			
			def provider(self):
		
				return self.__prov
			
			def properties(self):
		
				return self.__props
				
		def __init__(self):
		
			self.__proxies = {}
			
		def items(self):
		
			return self.__proxies.items()
			
		def get(self):
		
			try:
				proxy = self.__proxies[name]
			except KeyError:
				raise Exception("Platform '{}' does not exist".format(name))
			return proxy.get(name)
			
		def put(self, name, prov, props, state_res, printer_fact):
		
			if name in self.__proxies:
				raise Exception("Platform '{}' already exists".format(name))
			self.__proxies[name] = self.PlatformProxy(
				prov,
				props,
				state_res,
				printer_fact
			)
			
		def remove(self, name):
		
			del self.__proxies[name]
			
	class LayoutProxies:
	
		class LayoutProxy:
		
			def __init__(self, res, props):
			
				self.__inst = None
				self.__res = res
				self.__props = props or {}
			
			def get(self):
			
				if self.__inst is None:
					self.__inst = layout.Layout(
						self.resource(),
						self.properties()
					)
				return self.__inst
			
			def resource(self):
			
				return self.__res
			
			def properties(self):
			
				return self.__props
				
		def __init__(self):
		
			self.__proxies = {}
			
		def items(self):
		
			return self.__proxies.items()
			
		def get(self, name):
	
			try:
				proxy = self.__proxies[name]
			except KeyError:
				raise Exception("Layout '{}' does not exist".format(name))
			return proxy.get()
		
		def put(self, name, res, props):
	
			if name in self.__proxies:
				raise Exception("Layout '{}' already exists".format(name))
			self.__proxies[name] = self.LayoutProxy(res, props)
		
		def remove(self, name):
	
			del self.__proxies[name]
			
	def __init__(self, state_res):
	
		self.__state_res = state_res
		self.__platforms = self.PlatformProxies()
		self.__layouts = self.LayoutProxies()
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
					prov = data["provider"]
					props = data["properties"]
					self.__platforms.put(
						name,
						prov,
						props,
						self.__state_res,
						self.__printer_fact
					)
			if "layouts" in state:
				for name, data in state["layouts"].items():
					res = resource.ref(data["resource"])
					props = data["properties"]
					self.__layouts.put(name, res, props)
		except resource.ResourceNotFoundError:
			pass
		
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
			name: proxy.provider()
			for name, proxy in self.__platforms.items()
		}
		
	def layouts(self):
	
		return {
			name: proxy.resource().unref()
			for name, proxy in self.__layouts.items()
		}
		
	def register(self, name, prov, props=None):
	
		self.__platforms.put(
			name,
			prov,
			props,
			self.__state_res,
			self.__printer_fact
		)
		
	def dismiss(self, name, destroy):
	
		if destroy:
			self.__platforms.get(name).destroy()
		self.__platforms.remove(name)
		
	def offer(self, name, res, props=None):
	
		plat = self.__platforms.get(name)
		image = image.Image(res, props or {})
		plat.build(image)
		plat.publish(image)
		
	def retire(self, name, res):
	
		plat =  self.__platforms.get(name)
		image = image.Image(res, {})
		plat.delete(image)
		
	def bind(self, name, res, props=None):
	
		self.__layouts.put(name, res, props)
		
	def leave(self, name, destroy):
	
		if destroy:
			self__layouts.get(name).destroy()
		self.__layouts.remove(name)
		
	def store(self):
	
		state = {
			"platforms": {},
			"layouts": {}
		}
		for name, proxy in self.__platforms.items():
			state["platforms"][name] = {
				"provider": proxy.provider(),
				"properties": proxy.properties()
			}
		for name, proxy in self.__layouts.items():
			state["layouts"][name] = {
				"resource": proxy.resource().unref(),
				"properties": proxy.properties()
			}
		state_file = self.__state_res.open("w")
		jsons.write_dict(state_file, state, True)
		state_file.write("\n")
		state_file.close()

