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
import os
import os.path
import subprocess

def merge_dict(source, other):

	for key, value in other.items():
		try:
			source_value = source[key]
			if isinstance(source_value, list):
				source.extend(value)
			elif isinstance(source_value, dict):
				merge_dict(source_value, other)
			else:
				source[key] = other
		except KeyError:
			source[key] = value
			
def call(call_dir, args, err_msg):
	
	try:
		old_dir = None
		if call_dir is not None:
			old_dir = os.getcwd()
			os.chdir(call_dir)
			
		proc = subprocess.Popen(args)
		if proc.wait() != 0:
			raise RuntimeError(err_msg)
	except KeyboardInterrupt:
		try:
			cmd = ""
			sep = ""
			for arg in args:
				cmd = "{}{}{}".format(cmd, sep, arg)
				sep = " "
			proc.terminate()
			proc.wait()
		except KeyboardInterrupt:
			try:
				proc.kill()
				proc.wait()
			except KeyboardInterrupt:
				raise Exception("{} still running...".format(cmd))
		finally:
			raise Exception("{} execution aborted".format(cmd))
	finally:
		if old_dir is not None:
			os.chdir(old_dir)
			
def resolve(r_in, r_out, r_vars):

	class Resolver:

		def __init__(self, r_out, r_vars):
			self.__r_out = r_out
			self.__r_vars = r_vars
			self.__expr = io.StringIO()
			self.__update = self.__update_plain
		
		def update(self, c):
			self.__update(c)
		
		def __update_plain(self, c):
			if c == '#':
				self.__update = self.__update_sharp
			else:
				self.__r_out.write(c)
			
		def __update_sharp(self, c):
			if c == '{':
				self.__update = self.__update_expr
			else:
				if c == '#':
					self.__update = self.__update_sharpn
				else:
					self.__update = self.__update_plain
					self.__r_out.write('#')
				self.__r_out.write(c)
			
		def __update_sharpn(self, c):
			if c != '#':
				self.__update = self.__update_plain
			self.__r_out.write(c)
		
		def __update_expr(self, c):
			if c == '}':
				self.__update = self.__update_plain
				resolver = Resolver(self.__r_out, self.__r_vars)
				self.__expr.seek(0)
				for c in eval(self.__expr.read(), {}, self.__r_vars):
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
			
	resolver = Resolver(r_out, r_vars)
	c = r_in.read(1)
	while len(c) > 0:
		resolver.update(c)
		c = r_in.read(1)
		
def resolvable(obj, props):

	def resolvable_result(obj):
	
		if isinstance(obj, list):
			return ResolvableList(obj)
		if isinstance(obj, dict):
			return ResolvableDict(obj)
		if isinstance(obj, str):
			r_in = io.StringIO(obj)
			r_out = io.StringIO()
			resolve(r_in, r_out, props)
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
					
	class ExpressionDictIterator:

		def __init__(self, it):
		
			self.__it = it
			
		def __iter__(self):
		
			return self
		
		def __next__(self):
		
			return self.__it.__next__()
			
	return resolvable_result(obj)

