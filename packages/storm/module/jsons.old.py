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

class JSONInputStream:

	def __init__(self, str_in, key=None):
	
		self.__str_in = str_in
		self.__key = key
		
	def __read(self):
	
		return self.__str_in.read(1)
		
	def __ignore_nothing(self, c):
	
		return c
		
	def __ignore_separator(self, c):
	
		if len(c) == 0:
			raise Exception("Broken JSON")
		if c != ",":
			raise Exception("Illegal item separator '{}'".format(c))
		return self.__read_relevant()
		
	def __read_relevant(self):
	
		c = self.__read()
		while c.isspace():
			c = self.__read()
		return c
		
	def __value_number(self, first_c):
	
		str_io = io.StringIO()
		str_io.write(first_c)
		c = self.__read()
		while len(c) > 0 and not c.isspace():
			str_io.write(c)
			c = self.__read()
		str_io.seek(0)
		return eval(str_io.read())
		
	def __value_str(self, first_c):
	
		escape = False
		c = self.__read()
		while len(c) > 0:
			if escape:
				yield c
				escape = False
			elif c == "\\":
				yield c
				escape = True
			elif c == first_c:
				break;
			else:
				yield c
			c = self.__read()
			
		return None
		
	def __value_list(self):
	
		prepare_for_next = self.__ignore_nothing
		c = self.__read_relevant()
		while len(c) > 0 and c != "]":
			c = prepare_for_next(c)
			
			yield self.__value_item(c)
			
			prepare_for_next = self.__ignore_separator
			c = self.__read_relevant()
		
	def __value_dict(self):
	
		prepare_for_next = self.__ignore_nothing
		c = self.__read_relevant()
		while len(c) > 0 and c != "}":
			c = prepare_for_next(c)
			
			if c not in [ "'", "\"" ]:
				raise Exception("Invalid key delimiter '{}'".format(c))
			
			key = io.StringIO()
			for c in self.__value_str(c):
				key.write(c)
			key.seek(0)
			
			c = self.__read_relevant()
			if len(c) == 0 or c != ":":
				raise Exception("Invalid key-value separator '{}'".format(c))
				
			yield self.__value_item(c, key.read())
			
			prepare_for_next = self.__ignore_separator
			c = self.__read_relevant()
		
	def __value_item(self, first_c, key=None):
	
		if len(first_c) == 0:
			raise Exception("Broken JSON")
		if first_c in [ ",", "]", "}" ]:
			raise Exception("Illegal character '{}'".format(first_c))
		
		return JSONInputStream(self.__str_in, key)
			
	def key(self):
	
		return self.__key
		
	def value(self):
	
		c = self.__read_relevant()
		if len(c) > 0:
			if c in [ "]", "}" ]:
				raise Exception("Illegal character '{}'".format(c))
			
			if c in [ "'", "\"" ]:
				yield from self.__value_str(c)
			elif c == "[":
				yield from self.__value_list()
			elif c == "{":
				yield from self.__value_dict()
			else:
				yield self.__value_number(c)
				
	def value_str(self):
	
		str_io = io.StringIO()
		for c in self.value():
			str_io.write(c)
		str_io.seek(0)
		return str_io.read()
		
class JSONOutputStrean:

	def __init__(self, str_out):
	
		self.__str_out = str_out
		
	def start_dict(self, key=None):
	
		return JSONOutputStrean(self.__str_out)
		
	def end(self):
	
		pass

