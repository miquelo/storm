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
		
	def test_chaos_stream(self):
	
		str_in = io.StringIO("""
			"complete stream"
			{
				"number": 24,
				"color": "blue",
				"elements": [
					"string",
					{
						"name": "Mordecai"
					},
					1.25,
					[
					]
				],
				"empty dict": {
				}
			}
			[
				"a",
				"b",
				"c"
			]
		""")
		
		json_obj = jsons.read(str_in)
		self.assertTrue(json_obj.isstr())
		self.assertEqual(json_obj.value(), "complete stream")
		
		json_obj = jsons.read(str_in)
		self.assertTrue(json_obj.isdict())
		count_a = 0
		for item_a in json_obj:
			if count_a == 0:
				self.assertTrue(item_a.isnumber())
				self.assertEqual(item_a.key(), "number")
				self.assertEqual(item_a.value(), 24)
			elif count_a == 1:
				self.assertTrue(item_a.isstr())
				self.assertEqual(item_a.key(), "color")
				self.assertEqual(item_a.value(), "blue")
			elif count_a == 2:
				self.assertTrue(item_a.islist())
				self.assertEqual(item_a.key(), "elements")
				value_a = item_a.value()
				self.assertEqual(len(value_a), 4)
				self.assertEqual(value_a[0], "string")
				self.assertEqual(value_a[1]["name"], "Mordecai")
				self.assertEqual(value_a[2], 1.25)
				self.assertEqual(value_a[3], [])
			elif count_a == 3:
				self.assertTrue(item_a.isdict())
				self.assertEqual(item_a.key(), "empty dict")
				count_b = 0
				for item_b in item_a:
					count_b += 1
				self.assertEqual(count_b, 0)
			else:
				self.assertTrue(False, "Invalid length")
			count_a += 1
			
		json_obj = jsons.read(str_in)
		self.assertTrue(json_obj.islist())
		count_a = 0
		for item_a in json_obj:
			if count_a == 0:
				self.assertEqual(item_a.value(), "a")
			elif count_a == 1:
				self.assertEqual(item_a.value(), "b")
			elif count_a == 2:
				self.assertEqual(item_a.value(), "c")
			else:
				self.assertTrue(False, "Invalid length")
			count_a += 1

