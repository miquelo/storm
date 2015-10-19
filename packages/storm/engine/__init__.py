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

"""
Engine module.
"""

from storm.engine import layout

import concurrent.futures
import importlib

class Engine:

	"""
	The engine of the management tool.
	
	:param Resource state_res:
	   Resource holding the state of the engine.
	:param engine_dispatch_event_fn dispatch_event_fn:
	   Function called in order to dispatch an engine task event.
	:param TaskExecutor task_executor:
	   Executor used to run executor tasks.
	"""
	
	class __PlatformStubs:
	
		def __init__(self):
		
			self.__stubs = {}
			
		def items(self):
		
			return self.__stubs.items()
			
		def get(self, name):
		
			try:
				return self.__stubs[name]
			except KeyError:
				raise Exception("Platform '{}' does not exist".format(name))
				
		def put(self, name, prov, props, state_res):
		
			if name in self.__stubs:
				raise Exception("Platform '{}' already exists".format(name))
			data_res = state_res.parent().ref("platforms").ref(name)
			stub = self.__PlatformStub(prov, props, data_res)
			self.__stubs[name] = stub
			return stub
			
		def remove(self, name):
		
			stub = self.__stubs[name]
			del self.__stubs[name]
			return stub
			
	class __PlatformStub:
	
		def __init__(self, prov, props, data_res):
		
			self.__prov = props
			self.__props = props
			
			mod_name = "storm.provider.platform.{}".format(self.__prov)
			mod = importlib.import_module(mod_name)
			self.__inst = mod.Platform(data_res, self.__props)
			
		def provider(self):
		
			return self.__prov
			
		def properties(self):
		
			return self.__props
			
		def configure(self, context):
		
			return self.__inst.configure(context)
			
	class __PlatformTaskContext:
	
		def __init__(self, worker):
		
			self.__worker = worker
			
		def message(self, msg):
		
			self.__worker.message(msg)
			
		def progress(self, value):
		
			self.__worker.progress(value)
			
	class __EngineTask:
	
		def __init__(self, worker):
		
			self.__worker = worker
			
		def cancel(self):
		
			return self.__worker.cancel()
			
		def result(self, timeout=None):
		
			return self.__worker.result(timeout)
			
	class __EngineTaskWorker:
	
		def __init__(self, fire_event_fn, platform_tasks):
		
			self.__fire_event_fn = fire_event_fn
			self.__context = self.__PlatformTaskContext(self)
			self.__future = None
			self.__engine_task = None
			self.__platform_tasks = platform_tasks
			self.__completed_count = 0
			
		def __tasks_run(self):
		
			event = self.__EngineTaskStartedEvent(self.__engine_task)
			self.__fire_event_fn(event)
			for platform_task in self.__platform_tasks:
				platform_task.run(self.__context)
				self.__completed_count += 1
			event = self.__EngineTaskFinishedEvent(self.__engine_task)
			self.__fire_event_fn(event)
				
		def submit(self, executor):
		
			self.__engine_task = self.__EngineTask(self)
			self.__future = executor.submit(self.__tasks_run)
			return self.__engine_task
			
		def cancel(self):
		
			return self.__future.cancel()
			
		def result(self, timeout):
		
			return self.__future.result(timeout)
			
		def message(self, msg):
		
			event = self.__EngineTaskMessageEvent(self.__engine_task, msg)
			self.__fire_event_fn(event)
			
		def progress(self, value):
		
			task_count = len(self.__platform_taks)
			aggval = (self.__completed_count + value) / task_count
			event = self.__EngineTaskProgressEvent(self.__engine_task, aggval)
			self.__fire_event_fn(event)
			
	class __EngineTaskEvent:
	
		def __init__(self, task):
		
			self.__task = task
			
		@property
		def task(self):
		
			return self.__task
			
	class __EngineTaskStartedEvent(__EngineTaskEvent):
	
		def __init__(self, task):
		
			super().__init__(task)
			
	class __EngineTaskFinishedEvent(__EngineTaskEvent):
	
		def __init__(self, task):
		
			super().__init__(task)
			
	class __EngineTaskMessageEvent(__EngineTaskEvent):
	
		def __init__(self, task, msg):
		
			super().__init__(task)
			self.__msg = msg
			
		@property
		def message(self):
		
			return self.__msg
			
	class __EngineTaskProgressEvent(__EngineTaskEvent):

		def __init__(self, task, value):
		
			super().__init__(task)
			self.__value = value
			
		@property
		def value(self):
		
			return self.__value
			
	def __init__(
		self,
		state_res,
		dispatch_event_fn=None,
		task_executor=concurrent.futures.ThreadPoolExecutor(max_workers=10)
	):
	
		def fire_event_pass():
		
			pass
			
		self.__state_res = state_res
		self.__fire_event_fn = fire_event_fn or fire_event_pass
		self.__task_executor = task_executor
		self.__platforms = self.__PlatformStubs()
		
		try:
			state_file = self.__state_res.open("r")
			state_in = jsons.read(state_file)
			if state_in is None:
				state = {}
			else:
				state = state_in.value()
			state_file.close()
			
			if "platforms" in state:
				for name, data in state["platforms"].items():
					prov = data["provider"]
					props = data["properties"]
					self.__platforms.put(name, prov, props, self.__state_res)
		except resource.ResourceNotFoundError:
			pass
			
	def __engine_task(self, *platform_tasks):
	
		worker = self.__EngineTaskWorker(self.__fire_event_fn, platform_tasks)
		return worker.submit(self.__task_executor)
		
	def platforms(self):
	
		"""
		Returns a dictionary containing name/provider entries.
		"""
		
		return {
			name: stub.provider()
			for name, stub in self.__platforms.items()
		}
		
	def register(self, name, prov, props=None):
	
		stub = self.__platforms.put(name, prov, props, self.__state_res)
		return __engine_task(stub.configure())
		
	def store(self):
	
		state = {
			"platforms": {}
		}
		for name, stub in self.__platforms.items():
			state["platforms"][name] = {
				"provider": stub.provider(),
				"properties": stub.properties()
			}
		state_file = self.__state_res.open("w")
		jsons.write_dict(state_file, state, True)
		state_file.write("\n")
		state_file.close()

