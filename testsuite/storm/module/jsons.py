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

from storm.module import jsons

import io
import unittest

class TestRead(unittest.TestCase):

	def read_str(self, str_val):
	
		return jsons.read(io.StringIO(str_val))
		
	def test_empty(self):
	
		self.assertIsNone(self.read_str(""))
			
	def test_empty_list(self):
	
		json_obj = self.read_str("""
			[
			]
		""")
		self.assertTrue(json_obj.islist())
		count_a = 0
		for item_a in json_obj:
			count_a += 1
		self.assertEqual(count_a, 0)
				
	def test_empty_dict(self):
	
		json_obj = self.read_str("""
			{
			}
		""")
		self.assertTrue(json_obj.isdict())
		count_a = 0
		for item_a in json_obj:
			count_a += 1
		self.assertEqual(count_a, 0)
		
	def test_one_item_list(self):
	
		json_obj = self.read_str("""
			[
				"value"
			]
		""")
		self.assertTrue(json_obj.islist())
		count_a = 0
		for item_a in json_obj:
			count_a += 1
			self.assertTrue(item_a.isstr())
			self.assertIsNone(item_a.key())
			self.assertEqual(item_a.value(), "value")
		self.assertEqual(count_a, 1)
		
	def test_one_item_dict(self):
	
		json_obj = self.read_str("""
			{
				"key": "value"
			}
		""")
		self.assertTrue(json_obj.isdict())
		count_a = 0
		for item_a in json_obj:
			count_a += 1
			self.assertTrue(item_a.isstr())
			self.assertEqual(item_a.key(), "key")
			self.assertEqual(item_a.value(), "value")
		self.assertEqual(count_a, 1)
		
	def test_list_value(self):
	
		json_obj = self.read_str("""
			[
				"value"
			]
		""")
		self.assertTrue(json_obj.islist())
		val = json_obj.value()
		self.assertEqual(type(val), list)
		self.assertEqual(val[0], "value")
		
	def test_dict_value(self):
	
		json_obj = self.read_str("""
			{
				"key": "value"
			}
		""")
		self.assertTrue(json_obj.isdict())
		val = json_obj.value()
		self.assertEqual(type(val), dict)
		self.assertEqual(val["key"], "value")

