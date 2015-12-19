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

from storm import engine

import os
import subprocess

def execute(context, cmd_args, working_dir=None, wait_timeout=0.1):

	"""
	Executes a local system command within a platform task context.
	
	:param PlatformTaskContext context:
	   The platform task context.
	:param list cmd_args:
	   Command arguments.
	:param string working_dir:
	   Working directory. Current working directory if set to None.
	:param float wait_timeout:
	   Time in seconds between cancel checkings.
	:rtype:
	   int
	:return:
	   Error level code or None if execution was not completed.
	"""
	
	try:
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
			except engine.EngineTaskCancelled:
				proc.terminate()
				while True:
					try:
						context.cancel_check()
						return proc.wait(wait_timeout)
					except TimeoutExpired:
						pass
					except engine.EngineTaskCancelled:
						proc.kill()
						while True:
							try:
								context.cancel_check()
								return proc.wait(wait_timeout)
							except TimeoutExpired:
								pass
							except engine.EngineTaskCancelled:
								return None
	finally:
		if old_working_dir is not None:
			os.chdir(old_working_dir)

