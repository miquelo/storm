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

