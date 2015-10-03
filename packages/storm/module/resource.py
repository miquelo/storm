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

import importlib
import urllib.parse

default_scheme = "file"

class ResourceNotFoundError(BaseException):

	def __init__(self, args):
	
		super().__init__(args)
		
def ref(uri_str, props=None):

	class Resource:
	
		def __init__(self, mod, uri, props):
		
			if not mod.isabs(uri.path):
				if default_scheme == uri.scheme:
					url_parts = urllib.parse.SplitResult(
						uri.scheme,
						uri.location or "",
						mod.abspath(uri.path),
						uri.query or "",
						uri.fragment or ""
					)
					self.__uri = URI(url_parts)
				else:
					raise TypeError("Resource cannot have a relative path")
			else:
				self.__uri = uri

			self.__mod = mod
			self.__handler = mod.ResourceHandler(self.__uri, props)
			self.__props = props
			
		def __url_parts(self, path, query, fragment):
		
			return urllib.parse.SplitResult(
				self.__uri.scheme,
				self.__uri.location or "",
				path,
				query or self.__uri.query or "",
				fragment or self.__uri.fragment or ""
			)
			
		@property
		def scheme(self):
		
			return self.__uri.scheme
			
		@property
		def location(self):
		
			return self.__uri.location
			
		@property
		def path(self):
		
			return self.__uri.path
			
		@property
		def query(self):
		
			return self.__uri.query
			
		@property
		def fragment(self):
		
			return self.__uri.fragment
			
		def unref(self):
		
			return str(self.__uri)
			
		def ref(self, path, query=None, fragment=None):
		
			new_path = self.__mod.join(self.path, path)
			url_parts = self.__url_parts(new_path, query, fragment)
			return resource_ref(url_parts, self.__props)
			
		def parent(self, query=None, fragment=None):
		
			new_path = self.__mod.dirname(self.path)
			url_parts = self.__url_parts(new_path, query, fragment)
			return resource_ref(url_parts, self.__props)
			
		def exists(self):
		
			return self.__handler.exists()
			
		def name(self):
		
			return self.__handler.name()
			
		def delete(self):
		
			return self.__handler.delete()
			
		def open(self, flags):
		
			return self.__handler.open(flags)
			
	class URI:
	
		def __init__(self, url_parts):
		
			self.__url_parts = url_parts
			
		def __str__(self):
		
			return urllib.parse.urlunsplit(self.__url_parts)
			
		@property
		def scheme(self):
		
			return self.__url_parts[0]
			
		@property
		def location(self):
		
			if len(self.__url_parts[1]) > 0:
				return Location(self.__url_parts)
			return None
			
		@property
		def path(self):
		
			return self.__url_parts[2] or None
			
		@property
		def query(self):
		
			return self.__url_parts[3] or None
			
		@property
		def fragment(self):
		
			return self.__url_parts[4] or None
			
	class Location:
	
		def __init__(self, url_parts):
		
			self.__url_parts = url_parts
			
		def __str__(self):
		
			return self.__url_parts[1]
			
		@property
		def username(self):
		
			return self.__url_parts.username
			
		@property
		def password(self):
		
			return self.__url_parts.password
			
		@property
		def hostname(self):
		
			return self.__url_parts.hostname
			
		@property
		def port(self):
		
			return self.__url_parts.port
			
	def resource_ref(url_parts, props):
	
		uri = URI(url_parts)
		mod_name = "storm.provider.resource.{}".format(uri.scheme)
		return Resource(importlib.import_module(mod_name), uri, props)
		
	return resource_ref(urllib.parse.urlsplit(uri_str, default_scheme), props)

