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

