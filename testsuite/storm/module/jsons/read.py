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

	def test_empty(self):
	
		json_in = jsons.JSONInputStream(io.StringIO(""))
		for v in json_in.value():
			self.assertTrue(False)
			
	def test_empty_dict(self):
	
		json_in = jsons.JSONInputStream(io.StringIO("""
			{
			}
		"""))
		count = 0
		for v in json_in.value():
			count += 1
		self.assertEqual(count, 1)
			
	def test_empty_list(self):
	
		json_in = jsons.JSONInputStream(io.StringIO("""
			[
			]
		"""))
		for i, v in enumerate(json_in.value()):
			self.assertTrue(False)
			
	def test_one_item_list(self):
	
		json_in = jsons.JSONInputStream(io.StringIO("""
			[
				"value"
			]
		"""))
		for v in json_in.value():
			self.assertIsNone(v.key())
			self.assertEqual(v.value_str(), "value")
			
	def test_one_item_dict(self):
	
		json_in = jsons.JSONInputStream(io.StringIO("""
			{
				"key": "value"
			}
		"""))
		for v in json_in.value():
			self.assertEqual(v.key(), "key")
			self.assertEqual(v.value_str(), "value")

