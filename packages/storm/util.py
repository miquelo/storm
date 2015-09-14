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
		orig_cwd = os.getcwd()
		os.chdir(call_dir)
		res = subprocess.call(args)
		if res != 0:
			raise RuntimeError(err_msg)
	finally:
		os.chdir(orig_cwd)
	
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

