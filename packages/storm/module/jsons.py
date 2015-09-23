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
		self.__last = None
		self.__peek = self.__peek_from_str
		self.__read = self.__read_from_str
		
	def __ignore(self):
	
		 self.__read_from_str()
		
	def __ignore_nothing(self):
	
		pass
		
	def __ignore_separator(self):
	
		c = self.__peek_relevant()
		if c is None:
			raise Exception("Broken JSON")
		if c != ",":
			raise Exception("Illegal item separator '{}'".format(c))
		self.__ignore()
			
	def __peek_from_str(self):
	
		self.__last = self.__read_from_str()
		self.__peek = self.__peek_after_peek
		self.__read = self.__read_after_peek
		return self.__last
		
	def __peek_after_peek(self):
	
		return self.__last
		
	def __read_from_str(self):
	
		return self.__str_in.read(1)
		
	def __read_after_peek(self):
	
		self.__peek = self.__peek_from_str
		self.__read = self.__read_from_str
		return self.__last
		
	def __peek_relevant(self):
	
		c = self.__peek()
		while c is not None and c.isspace():
			self.__ignore()
			c = self.__peek()
		return c
		
	def __value_number(self):
	
		str_io = io.StringIO()
		c = self.__peek()
		while c is not None and not c.isspace():
			self.__ignore()
			str_io.write(c)
			c = self.__peek()
		return eval(str_io.read())
		
	def __value_str(self):
	
		limit_c = self.__read()
		escape = False
		c = self.__read()
		while c is not None:
			if escape:
				yield c
				escape = False
			elif c == "\\":
				yield c
				escape = True
			elif c == limit_c:
				break;
			else:
				yield c
			c = self.__read()
			
		return None
		
	def __value_list(self):
	
		self.__ignore() # Ignore "[" character
		
		prepare_for_next = self.__ignore_nothing
		c = self.__peek_relevant()
		while c is not None and c != "]":
			prepare_for_next(self)
			
			yield self.__value_item(self)
			
			prepare_for_next = self.__ignore_separator
			c = self.__peek_relevant()
		self.__ignore()
		
	def __value_dict(self):
	
		self.__ignore() # Ignore "{" character
		
		prepare_for_next = self.__ignore_nothing
		c = self.__peek_relevant()
		while c is not None and c != "}":
			prepare_for_next(self)
			
			key = io.StringIO()
			for c in self.__value_str():
				key.write(c)
				
			yield self.__value_item(self)
				
			prepare_for_next = self.__ignore_separator
			c = self.__peek_relevant()
		self.__ignore()
		
	def __value_item(self):
	
		c = self.__peek_relevant()
		if c is None:
			raise Exception("Broken JSON")
		if c in [ ",", "]", "}" ]:
			raise Exception("Illegal character '{}'".format(c))
		return JSONInputStream(self.__str_in)
			
	def key(self):
	
		return self.__key
		
	def value(self):
	
		c = self.__peek_relevant()
		if c is None:
			return None
		if c in [ "'", "\"" ]:
			yield from self.__value_str()
		if c == "[":
			yield from self.__value_list()
		if c == "{":
			yield from self.__value_dict()
		if c in [ "]", "}" ]:
			raise Exception("Illegal character '{}'".format(c))
		return self.__value_number()

