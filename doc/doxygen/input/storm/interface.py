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

##
# @package storm.interface
# Public interfaces.
#

##
# Function for @link storm.interface.EngineTask @endlink event handling.
#
# @param event
#		Event object of type @link storm.interface.EngineTaskEvent @endlink.
#
def executor_fire_event_fn(event):

	pass
	
##
# Task executor function.
#
# @return
#		Result value.
#
def task_executor_fn():

	pass

##
# Scheduled engine task.
#
class EngineTask:

	##
	# Wait for a task completion and return its result value.
	#
	# @param timeout
	#		Wait timeout.
	#
	# @return
	#		Result value.
	#
	def result(self, timeout):
	
		pass
		
##
# Engine task event.
#
class EngineTaskEvent:

	##
	# Source task of type @link storm.interface.EngineTask @endlink.
	#
	@property
	def task(self):
	
		pass
		
##
# Engine task started event.
#
class EngineTaskStartedEvent(EngineTaskEvent):

	pass
	
##
# Engine task finished event.
#
class EngineTaskFinishedEvent(EngineTaskEvent):

	pass
	
##
# Engine task message event.
#
class EngineTaskMessageEvent(EngineTaskEvent):

	##
	# Event message.
	#
	@property
	def message(self):
	
		pass
		
##
# Engine task message event.
#
class EngineTaskProgressEvent(EngineTaskEvent):

	##
	# Progress value.
	#
	@property
	def value(self):
	
		pass
		
##
# Future.
#
class Future:

	pass
	
##
# Task executor.
#
class TaskExecutor:

	##
	# Submit a task to be executed.
	#
	# @param task_fn
	#		A function implementing @link storm.interface.task_executor_fn
	#		@endlink.
	#
	# @return
	#		An object implementing @link storm.interface.Future @endlink.
	#
	def submit(self, task_fn):
	
		pass

