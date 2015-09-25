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

import io

def read_from(str_in):

	class JSONObject:
	
		def __init__(self, key):
		
			self.__key = key
			
		def __str__(self):
		
			return str(self.value())
			
		def key(self):
		
			return self.__key
			
		def isnumber(self):
		
			return False
			
		def isstr(self):
		
			return False
			
		def islist(self):
		
			return False
			
		def isdict(self):
		
			return False
			
		def started(self):
		
			
	class JSONNumber(JSONObject):
	
		def __init__(self, key, first_char, str_in):
		
			super().__init__(key)
			self.__started = False
			self.__first_char = first_char
			self.__str_in = str_in
			self.__iter = self.__iter_first
			
		def __iter__(self):
		
			yield from self.__iter()
			
		def __iter_first(self):
		
			self.__started = True
			self.__iter = self.__iter_next
			yield self.__first_char
			
		def __iter_next(self):
		
			completed_check(self)
			c = self.__str_in.read(1)
			if len(c) is None or c.isspace():
				self.__str_in = None
				raise StopIteration()
			# TODO When c in (",", "]", "}")
			yield c
			
		def isnumber(self):
		
			return True
			
		def started(self):
		
			return self.__started
			
		def completed(self):
		
			return self.__str_in is not None
			
		def value(self):
		
			started_check(self)
			str_io = io.StringIO(self.__first_char)
			for c in self:
				str_io.write(c)
			self.__str_in = None
			str_io.seek(0)
			value = eval(str_io.read())
			if type(value) not in (int, long, float, complex):
				raise Exception("'{}' ia not a number".format(value))
			return value
			
	class JSONString(JSONObject):
	
		def __init__(self, key, delim, str_in):
		
			super().__init__(key)
			self.__started = False
			self.__delim = delim
			self.__str_in = str_in
			self.__iter = self.__iter_first
			
		def __iter__(self):
		
			completed_check(self)
			self.__started = True
			yield from str_generator(self.__str_in, self.__delim)
			self.__str_in = None
			
		def isstr(self):
		
			return True
			
		def started(self):
		
			return self.__started
			
		def completed(self):
		
			return self.__str_in is not None
			
		def value(self):
		
			started_check(self)
			str_io = io.StringIO()
			for c in self:
				str_io.write(c)
			return str_io.read()
			
	class JSONList(JSONObject):
	
		def __init__(self, key, str_in):
		
			super().__init__(key)
			self.__started = False
			self.__str_in = str_in
			
		def __iter__(self):
		
			completed_check(self)
			self.__started = True
			c = read_next(self.__str_in)
			while len(c) > 0:
				yield get_item(None, c, self.__str_in)
				c = read_item_next(self.__str_in, "]")
				
		def islist(self):
		
			return True
			
		def started(self):
		
			return self.__started
			
		def completed(self):
		
			return self.__str_in is not None
			
	class JSONDictionary(JSONObject):
	
		def __init__(self, key, str_in):
		
			super().__init__(key)
			self.__started = False
			self.__str_in = str_in
			
		def __iter__(self):
		
			completed_check(self)
			self.__started = True
			c = read_next(self.__str_in)
			while len(c) > 0:
				if c not in ( "'", "\"" ):
					raise Exception("Invalid key delimiter '{}'".format(c))
				key = io.StringIO()
				for c in str_generator(self.__str_in, c):
					key.write(c)
				key.seek(0)
				
				c = read_next(self.__str_in)
				if len(c) == 0 or c != ":":
					raise Exception("Invalid entry separator '{}'".format(c))
				
				yield get_item(key.read(), c, self.__str_in)
				c = read_item_next(self.__str_in, "}")
				
		def isdict(self):
		
			return True
			
		def started(self):
		
			return self.__started
			
		def completed(self):
		
			return self.__str_in is not None
			
	def started_check(json_obj):
	
		if json_obj.started():
			raise Exception("Read operation already started")
			
	def completed_check(json_obj):
	
		if json_obj.completed():
			raise Exception("Read operation already completed")
			
	def str_generator(str_in, delim):
	
		completed = False
		c = str_in.read(1)
		while len(c) > 0 and not completed:
			if c == delim:
				completed = True
			if c == '\\':
				escaped = str_in.read(1)
				if len(escaped) == 0:
					raise Exception("Incomplete escaped character")
				yield eval("\\{}".format(c))
			else:
				yield c
			c = str_in.read(1)
			
		if not completed:
			raise Exception("Incompleted character string")
			
	def read_next(str_in):
	
		c = str_in.read()
		while c.isspace():
			c = str_in.read()
		return c
		
	def read_item_next(str_in, close_char):
	
		c = read_next(self.__str_in)
		if len(c) == 0 or c == close_char:
			raise StopIteration()
		if c != ",":
			raise Exception("Illegal item separator '{}'".format(c))
		return read_next(self.__str_in)
		
	def get_item(key, first_char, str_in):
	
		# TODO When first_char in ("]", "}")
		if len(first_char) == 0:
			raise StopIteration()
		if first_char in ( "'", "\"" ):
			return JSONString(key, first_char, str_in)
		if first_char == "[":
			return JSONList(key, str_in)
		if first_char == "{":
			return JSONDictionary(key, str_in)
		return JSONNumber(key, first_char, str_in)
		
	c = str_in.read(1)
	return get_item(None, c, str_in)

