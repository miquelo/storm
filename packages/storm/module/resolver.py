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

"""
Resolver module.
"""

def resolve(r_in, r_out, r_vars):

	"""
	Reads from r_in and writes to r_out by resolving variables defined in
	r_vars.
	
	:param r_in:
	   Input source.
	:param r_out:
	   Output target.
	:param r_vars:
	   Variables for resolving.
	"""
	
	class Resolver:
	
		def __init__(self):
		
			self.__expr = io.StringIO()
			self.__update = self.__update_plain
			
		def update(self, c):
		
			self.__update(c)
			
		def __update_plain(self, c):
		
			if c == '#':
				self.__update = self.__update_sharp
			else:
				r_out.write(c)
				
		def __update_sharp(self, c):
		
			if c == '{':
				self.__update = self.__update_expr
			else:
				if c == '#':
					self.__update = self.__update_sharpn
				else:
					self.__update = self.__update_plain
					r_out.write('#')
				r_out.write(c)
				
		def __update_sharpn(self, c):
		
			if c != '#':
				self.__update = self.__update_plain
			r_out.write(c)
			
		def __update_expr(self, c):
		
			if c == '}':
				self.__update = self.__update_plain
				resolver = Resolver()
				self.__expr.seek(0)
				for c in eval(self.__expr.read(), {}, r_vars):
					resolver.update(c)
				self.__expr = io.StringIO()
			else:
				if c == '\'':
					self.__update = self.__update_expr_quot
				self.__expr.write(c)
				
		def __update_expr_quot(self, c):
		
			if c == '\'':
				self.__update = self.__update_expr
			self.__expr.write(c)
			
	resolver = Resolver()
	c = r_in.read(1)
	while len(c) > 0:
		resolver.update(c)
		c = r_in.read(1)
		
def resolvable(obj, props):

	"""
	Return the given object as a resolvable object.
	
	:param obj:
	   Object to be transformed to a resolvable object.
	:param props:
	   Resolve properties.
	:return:
	   Object as a resolvable object.
	"""
	
	def resolvable_result(obj):
			
		if isinstance(obj, list):
			return ResolvableList(obj)
		if isinstance(obj, dict):
			return ResolvableDict(obj)
		if isinstance(obj, str):
			r_in = io.StringIO(obj)
			r_out = io.StringIO()
			resolver.resolve(r_in, r_out, props)
			r_out.seek(0)
			return r_out.read()
		return obj
		
	class ResolvableList(list):
	
		def __init__(self, obj):
		
			self.extend(obj)
			
		def __getitem__(self, key):
		
			return resolvable_result(super().__getitem__(key))
			
		def __iter__(self):
		
			return ResolvableListIterator(super().__iter__())
			
		def __reversed__(self):
		
			return ResolvableListIterator(super().__reversed__())
			
	class ResolvableListIterator:
	
		def __init__(self, it):
		
			self.__it = it
			
		def __iter__(self):
		
			return self
			
		def __next__(self):
		
			return resolvable_result(self.__it.__next__())
			
	class ResolvableDict(dict):
	
		def __init__(self, obj):
		
			self.update(obj)
			
		def __getitem__(self, key):
		
			return resolvable_result(super().__getitem__(key))
			
		def __iter__(self):
		
			return ResolvableDictIterator(super().__iter__())
			
		def __reversed__(self):
		
			return ResolvableDictIterator(super().__reversed__())
			
		def items(self):
		
			return [
				(key, resolvable_result(value))
				for key, value in super().items()
			]
			
	class ResolvableDictIterator:
	
		def __init__(self, it):
		
			self.__it = it
			
		def __iter__(self):
		
			return self
			
		def __next__(self):
		
			return self.__it.__next__()
			
	return resolvable_result(obj)

