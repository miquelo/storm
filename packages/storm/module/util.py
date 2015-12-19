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

