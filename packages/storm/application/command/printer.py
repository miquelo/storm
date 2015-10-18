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
import io

class PrinterFactory:

	def __init__(self):
	
		try:
			self.__level = 0
			self.__colorama = importlib.import_module("colorama")
			self.__colorama.init()
			self.__printer = self.__printer_colorama
		except:
			self.__printer = self.__printer_default
			
	@property
	def level(self):
	
		return self.__level
	
	@level.setter
	def level(self, value):
	
		self.__level = value
		
	def printer(self, out):
	
		return self.__printer(out)
		
	def __printer_default(self, out):
	
		return PrinterDefault(out, self.__level)
		
	def __printer_colorama(self, out):
	
		return PrinterColorama(out, self.__level, self.__colorama)
		
		
class PrinterBase:

	def __init__(self, out, level):
	
		self.__out = out
		self.__level = level
		self.__buffer = io.StringIO()
		
	def append(self, text):
	
		self.__buffer.write(text)
		return self
		
	def print(self, level=0):
	
		self.__buffer.seek(0)
		if level <= self.__level:
			text = self.__buffer.read()
			self.__out.write(text)
			if len(text) > 0:
				self.__out.write("\n")
		self.__buffer = io.StringIO()
		return self

class PrinterDefault(PrinterBase):

	def __init__(self, out, level):
	
		super().__init__(out, level)
			
	def append(self, text, color=None, style=None):
	
		return super().append(text)
		
class PrinterColorama(PrinterBase):
	
	def __init__(self, out, level, colorama):
	
		super().__init__(out, level)
		self.__colorama = colorama
		
	def __color_code(self, color):
	
		expr = "colorama.Fore.{}".format(color.upper())
		return eval(expr, None, { "colorama": self.__colorama })
		
	def __style_code(self, style):
	
		expr = "colorama.Style.{}".format(style.upper())
		return eval(expr, None, { "colorama": self.__colorama })
		
	def append(self, text, color=None, style=None):
	
		tbeg = ""
		tend = ""
		try:
			tbeg = "{}".format(self.__color_code(color))
			tend = "{}".format(self.__colorama.Fore.RESET)
		except:
			pass
		try:
			tbeg = "{}{}".format(tbeg, self.__style_code(style))
			tend = "{}{}".format(self.__colorama.Style.RESET_ALL, tend)
		except:
			pass
		return super().append("{}{}{}".format(tbeg, text, tend))

