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

def read(str_in):

	class JSONInput:
	
		def __init__(self, str_in):
		
			self.__str_in = str_in
			self.__last = None
			self.peek = self.__peek_input
			
		def __peek_last(self):
		
			return self.__last
			
		def __peek_input(self):
		
			self.__last = self.__str_in.read(1)
			self.peek = self.__peek_last
			return self.__last
			
		def ignore(self):
		
			self.peek = self.__peek_input
			
		def read(self):
		
			c = self.peek()
			self.ignore()
			return c
			
		def peek_next(self):
		
			c = self.peek()
			while c.isspace():
				self.ignore()
				c = self.peek()
			return c
			
		def read_next(self):
		
			c = self.peek_next()
			self.ignore()
			return c
			
	class JSONObject:
	
		def __init__(self, key):
		
			self.__key = key
			
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
			
	class JSONNumber(JSONObject):
	
		def __init__(self, key, json_in):
		
			super().__init__(key)
			self.__json_in = json_in
			
		def isnumber(self):
		
			return True
			
		def value(self):
		
			str_io = io.StringIO()
			end = False
			c = self.__json_in.peek()
			while not end:
				if len(c) == 0 or c.isspace() or c in ( ",", "]", "}" ):
					end = True
				else:
					self.__json_in.ignore()
					str_io.write(c)
					c = self.__json_in.peek()
			str_io.seek(0)
			num_val = eval(str_io.read())
			if type(num_val) not in ( int, float, complex ):
				raise Exception("Value '{}' is not a number".format(num_val))
			return num_val
			
	class JSONString(JSONObject):
	
		def __init__(self, key, json_in):
		
			super().__init__(key)
			self.__json_in = json_in
			
		def __iter__(self):
		
			yield from str_value(self.__json_in)
				
		def isstr(self):
		
			return True
			
		def value(self):
		
			str_io = io.StringIO()
			for c in self:
				str_io.write(c)
			str_io.seek(0)
			return str_io.read()
			
	class JSONList(JSONObject):
	
		def __init__(self, key, json_in):
		
			super().__init__(key)
			self.__json_in = json_in
			
		def __iter__(self):
		
			yield from item_iter(self.__json_in, "]", item_key_read_list)
					
		def islist(self):
		
			return True
			
		def value(self):
		
			val = []
			for item in self:
				val.append(item.value())
			return val
			
	class JSONDictionary(JSONObject):
	
		def __init__(self, key, json_in):
		
			super().__init__(key)
			self.__json_in = json_in
			
		def __iter__(self):
		
			yield from item_iter(self.__json_in, "}", item_key_read_dict)
				
		def isdict(self):
		
			return True
			
		def value(self):
		
			val = {}
			for item in self:
				val[item.key()] = item.value()
			return val
			
	def str_value(json_in):
	
		delim = json_in.read()
		end = False
		while not end:
			c = json_in.read()
			if len(c) == 0:
				raise Exception("Unterminated character string")
			if c == delim:
				end = True
			elif c == '\\':
				esc_c = json_in.read()
				if len(esc_c) == 0:
					raise Exception("Unterminated character string")
				yield eval("\\{}".format(esc_c))
			else:
				yield c
			
	def item_read(key, json_in):
		
		c = json_in.peek_next()
		if len(c) == 0:
			raise Exception("Unexpected end of stream")
		if c in ( "'", "\"" ):
			return JSONString(key, json_in)
		if c == "[":
			json_in.ignore()
			return JSONList(key, json_in)
		if c == "{":
			json_in.ignore()
			return JSONDictionary(key, json_in)
		if c in ( "+", "-", "." ) or c.isdigit():
			return JSONNumber(key, json_in)
		raise Exception("Illegal item initial character '{}'".format(c))
		
	def item_iter(json_in, end_char, item_key_read):
	
		ready = True
		end = False
		while not end:
			c = json_in.peek_next()
			if c == ",":
				if ready:
					raise Exception("Empty item")
				else:
					json_in.ignore()
					c = json_in.peek_next()
					ready = True
			elif c == end_char:
				json_in.ignore()
				end = True
			elif not ready:
				raise Exception("Missing item separator")
			else:
				key = item_key_read(json_in)
				yield item_read(key, json_in)
				ready = False
		
	def item_key_read_list(json_in):
	
		return None
		
	def item_key_read_dict(json_in):
	
		c = json_in.peek_next()
		if c not in ( "'", "\"" ):
			raise Exception("Illegal key delimiter '{}'".format(c))
			
		key_io = io.StringIO()
		for c in str_value(json_in):
			key_io.write(c)
		key_io.seek(0)
		
		c = json_in.read_next()
		if c != ":":
			raise Execption("Missing key-value separator")
		
		return key_io.read()
		
	json_in = JSONInput(str_in)
	c = json_in.peek_next()
	if len(c) == 0:
		return None
	return item_read(None, json_in)
	
def write_number(str_out, value):

	if type(value) in ( int, float, complex ):
		str_out.write(str(value))
		return None
	raise Exception("Value '{}' is not a number".format(value))
	
def write_str(str_out, value=None):

	class JSONString:
	
		def __init__(self, str_out):
		
			self.__str_out = str_out
			self.__str_out.write("\"")
			
		def write(self, c):
		
			escape = c == "\""
			if escape:
				res_c = "\\{}".format(c)
			else:
				res_c = c
			self.__str_out.write(res_c)
			
		def close(self):
		
			self.__str_out.write("\"")
			
	if value is None:
		return JSONString(str_out)
	if isinstance(value, str):
		json_str = JSONString(str_out)
		for c in value:
			json_str.write(c)
		json_str.close()
		return None
	raise Exception("Value '{}' is not an string".format(value))
	
def write_list(str_out, value=None):

	class JSONList:
	
		def __init__(self, str_out):
		
			self.__str_out = str_out
			self.__write_ready = self.__write_ready_first
			self.__str_out.write("[")
			
		def __write_ready_first(self):
		
			self.__write_ready = self.__write_ready_next
			
		def __write_ready_next(self):
		
			self.__str_out.write(",")
			
		def write_number(self, value):
		
			self.__write_ready()
			return write_number(self.__str_out, value)
			
		def write_str(self, value=None):
		
			self.__write_ready()
			return write_str(self.__str_out, value)
			
		def write_list(self, value=None):
		
			self.__write_ready()
			return write_list(self.__str_out, value)
			
		def write_dict(self, value=None):
		
			self.__write_ready()
			return write_dict(self.__str_out, value)
			
		def close(self):
		
			self.__str_out.write("]")
			
	if value is None:
		return JSONList(str_out)
	if isinstance(value, list):
		json_list = JSONList(str_out)
		for item in value:
			if isinstance(item, ( int, float, complex )):
				json_list.write_number(item)
			elif isinstance(item, str):
				json_list.write_str(item)
			elif isinstance(item, list):
				json_list.write_list(item)
			elif isinstance(item, dict):
				json_list.write_dict(item)
			else:
				item_type = type(value)
				raise Exception("Unsupported JSON type '{}'".format(item_type))
		json_list.close()
		return None
	raise Exception("Value '{}' is not a list".format(value))
	
def write_dict(str_out, value=None):

	class JSONDictionary:
	
		def __init__(self, str_out):
		
			self.__str_out = str_out
			self.__write_ready = self.__write_ready_first
			self.__str_out.write("{")
			
		def __write_key(self, key):
		
			self.__write_ready()
			self.__str_out.write("\"{}\":".format(key))
			
		def __write_ready_first(self):
		
			self.__write_ready = self.__write_ready_next
			
		def __write_ready_next(self):
		
			self.__str_out.write(",")
			
		def write_number(self, key, value):
		
			self.__write_key(key)
			return write_number(self.__str_out, value)
			
		def write_str(self, key, value=None):
		
			self.__write_key(key)
			return write_str(self.__str_out, value)
			
		def write_list(self, key, value=None):
		
			self.__write_key(key)
			return write_list(self.__str_out, value)
			
		def write_dict(self, key, value=None):
		
			self.__write_key(key)
			return write_dict(self.__str_out, value)
			
		def close(self):
		
			self.__str_out.write("}")
			
	if value is None:
		return JSONDictionary(str_out)
	if isinstance(value, dict):
		json_dict = JSONDictionary(str_out)
		for key, val in value.items():
			if isinstance(val, ( int, float, complex )):
				json_dict.write_number(key, val)
			elif isinstance(val, str):
				json_dict.write_str(key, val)
			elif isinstance(val, list):
				json_dict.write_list(key, val)
			elif isinstance(val, dict):
				json_dict.write_dict(key, val)
			else:
				val_type = type(val)
				raise Exception("Unsupported JSON type '{}'".format(val_type))
		json_dict.close()
		return None
	raise Exception("Value '{}' is not a dictionary".format(value))

