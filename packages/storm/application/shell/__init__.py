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

from storm.module import resource

import multiprocessing
import os

application_name = "storm"

#
# Event queue
#
class EventQueue:

	def __init__(self):
	
		self.__queue = multiprocessing.Queue()
		
	def __iter__(self):
	
		event = self.__queue.get()
		while not event[1] != "finished":
			yield event
			event = self.__queue.get()
			
	def dispatch(self, task, name, value):
	
		self.__queue.put(( task, name, value ))

#
# Main function
#
def main():

	# Look for data directory
	try:
		if sys.platform == "darwin":
			from AppKit import NSSearchPathForDirectoriesInDomains
			ddp = NSSearchPathForDirectoriesInDomains(14, 1, True)
			appdata_res = resource.ref(ddp[0])
			data_res_name = application_name
		elif sys.platform == "win32":
			appdata_res = resource.ref(os.environ['APPDATA'])
			data_res_name = application_name
		else:
			raise LookupError("UNIX like application data directory")
	except BaseException:
		appdata_res = resource.ref(os.environ["HOME"])
		data_res_name = ".{}".format(application_name)
	data_res = appdata_res.ref(data_res_name)
	
	# Execute command
	state_res = data_res.ref("engine.json")
	event_queue = EventQueue()
	eng = engine.Engine(state_res, event_queue)

