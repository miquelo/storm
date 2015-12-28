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

class ProcessCancelled(Exception):

	"""
	Raised when process execution is cancelled.
	"""
	
	def __init__(self, args):
	
		super().__init__(args)
		
def merge_dict(source, other):

	"""
	Merge recursively the source object with the other object, by extending
	lists and inserting or replacing dictionary entries.
	
	:param source:
	   Source object.
	:param other:
	   Object to be merged to the source.
	"""
	
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
			
def execute(context, cmd_args, wait_timeout=0.1):

	"""
	Executes a local system command within a process context.
	
	:param ProcessContext context:
	   The process context.
	:param list cmd_args:
	   Command arguments.
	:param float wait_timeout:
	   Time in seconds between cancel checkings.
	:rtype:
	   int
	:return:
	   Error level code or None if execution was not completed.
	"""
	
	try:
		working_dir = context.working_dir()
		old_working_dir = None
		if working_dir is not None:
			old_working_dir = os.getcwd()
			os.chdir(working_dir)
			
		proc = subprocess.Popen(
			cmd_args,
			stdout=context.out(),
			stderr=context.err()
		)
		while True:
			try:	
				context.cancel_check()
				return proc.wait(wait_timeout)
			except TimeoutExpired:
				pass
			except ProcessCancelled:
				proc.terminate()
				while True:
					try:
						context.cancel_check()
						return proc.wait(wait_timeout)
					except TimeoutExpired:
						pass
					except ProcessCancelled:
						proc.kill()
						while True:
							try:
								context.cancel_check()
								return proc.wait(wait_timeout)
							except TimeoutExpired:
								pass
							except ProcessCancelled:
								return None
	finally:
		if old_working_dir is not None:
			os.chdir(old_working_dir)

