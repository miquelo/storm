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

from storm.module import jsons
from storm.module import resource

import concurrent.futures
import importlib

class Engine:

	"""
	The engine of the management tool.
	
	:param Resource state_res:
	   Resource holding the state of the engine.
	:param EngineEventQueue event_queue:
	   Event queue used for dispatching engine task events.
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
			stub = self.__PlatformStub(prov, data_res, props)
			self.__stubs[name] = stub
			return stub
			
		def remove(self, name):
		
			stub = self.__stubs[name]
			del self.__stubs[name]
			return stub
			
	class __PlatformStub:
	
		def __init__(self, prov, data_res, props):
		
			self.__prov = props
			self.__props = props
			
			mod_name = "storm.provider.platform.{}".format(self.__prov)
			mod = importlib.import_module(mod_name)
			self.__platform = mod.Platform(data_res, self.__props)
			
		def provider(self):
		
			return self.__prov
			
		def properties(self):
		
			return self.__props
			
		def configure(self):
		
			return self.__platform.configure()
			
		def destroy(self):
		
			return self.__platform.destroy()
			
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
			
		def result(self, timeout=None):
		
			return self.__worker.result(timeout)
			
		def cancel(self):
		
			return self.__worker.cancel()
			
	class __EngineTaskWorker:
	
		def __init__(self, event_queue, platform_tasks):
		
			self.__event_queue = event_queue
			self.__context = self.__PlatformTaskContext(self)
			self.__future = None
			self.__engine_task = None
			self.__platform_tasks = platform_tasks
			self.__completed_count = 0
			
		def __dispatch_event(self, name, value=None):
		
			self.__event_queue.dispatch(self.__engine_task, name, value)
			
		def __tasks_run(self):
		
			result = []
			self.__dispatch_event("started")
			for platform_task in self.__platform_tasks:
				result.append(platform_task.run(self.__context))
				self.__completed_count += 1
			self.__dispatch_event("finished")
			return result
				
		def submit(self, executor):
		
			self.__engine_task = self.__EngineTask(self)
			self.__future = executor.submit(self.__tasks_run)
			return self.__engine_task
			
		def result(self, timeout):
		
			return self.__future.result(timeout)
			
		def cancel(self):
		
			return self.__future.cancel()
			
		def message(self, msg):
		
			self.__dispatch_event("message", msg)
			
		def progress(self, value):
		
			task_count = len(self.__platform_taks)
			event_value = (self.__completed_count + value) / task_count
			self.__dispatch_event("progress", event_value)
			
	def __init__(
		self,
		state_res,
		event_queue=None,
		task_executor=concurrent.futures.ThreadPoolExecutor(max_workers=10)
	):
	
		class IgnoreEventQueue():
		
			def dispatch(self, task, name, value):
			
				pass
				
		self.__state_res = state_res
		self.__event_queue = event_queue or IgnoreEventQueue()
		self.__task_executor = task_executor
		self.__platform_stubs = self.__PlatformStubs()
		
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
					self.__platform_stubs.put(name, prov, props, state_res)
		except resource.ResourceNotFoundError:
			pass
			
	def __engine_task(self, plat_tasks):
	
		worker = self.__EngineTaskWorker(self.__event_queue, plat_tasks)
		return worker.submit(self.__task_executor)
		
	def platforms(self):
	
		"""
		Returns a dictionary containing name/provider entries.
		"""
		
		return {
			name: stub.provider()
			for name, stub in self.__platform_stubs.items()
		}
		
	def register(self, name, prov, props=None):
	
		"""
		Register a new platform with the given name implemented by the given
		provider.
		
		:param string name:
		   The name of the registered platform.
		:param string prov:
		   The provider name which implements the registered platform.
		:param dict props:
		   Optional properties dictionary.
		:rtype:
		   EngineTask
		:return:
		   The task running the registration process.
		:raises Exception:
		   If a platform with the given name already exists.
		"""
		
		stub = self.__platform_stubs.put(name, prov, props, self.__state_res)
		plat_tasks = []
		plat_tasks.append(stub.configure())
		return self.__engine_task(plat_tasks)
		
	def dismiss(self, name, destroy=False):
	
		"""
		Dismiss a registered platform.
		
		:param string name:
		   The name of the platform to be dismissed.
		:param bool destroy:
		   If the platform must be destroyed.
		:rtype:
		   EngineTask
		:return:
		   The task running the dismiss process.
		:raises Exception:
		   If the platform with the given name does not exist.
		"""
		
		stub = self.__platform_stubs.get(name)
		plat_tasks = []
		if destroy:
			plat_tasks.append(stub.destroy())
		return self.__engine_task(plat_tasks)
		
	def offer(self, name, image):
	
		"""
		Build and publish the given image to the given platform.
		
		:param string name:
		   Name of the platform.
		:param storm.engine.image.Image image:
		   The image to be built and published.
		:rtype:
		   EngineTask
		:return:
		   The task running the offer process.
		:raises Exception:
		   If the platform with the given name does not exist.
		"""
		
		stub = self.__platform_stubs.get(name)
		plat_tasks = []
		plat_tasks.append(stub.image_build(image))
		plat_tasks.append(stub.image_publish(image))
		return self.__engine_task(plat_tasks)
		
	def retire(self, name, image):
	
		"""
		Remove and unpublish the given image from the given platform.
		
		:param string name:
		   Name of the platform.
		:param storm.engine.image.Image image:
		   The image to be removed and unpublished.
		:rtype:
		   EngineTask
		:return:
		   The task running the retire process.
		:raises Exception:
		   If the platform with the given name does not exist.
		"""
		
		stub = self.__platform_stubs.get(name)
		plat_tasks = []
		plat_tasks.append(stub.image_remove(image))
		plat_tasks.append(stub.image_unpublish(image))
		return self.__engine_task(plat_tasks)
		
	def satisfy(self, layout):
	
		"""
		Try to do layout be in the given state accross platforms.
		
		:param storm.engine.layout.Layout layout:
		   The layout to be put into construction.
		:rtype:
		   EngineTask
		:return:
		   The task running the maintain process.
		"""
		
		stub = self.__platform_stubs.get(name)
		plat_tasks = []
		plat_tasks.append(stub.construction(layout))
		return self.__engine_task(plat_tasks)
		
	def store(self):
	
		"""
		Store the current engine state to the state resource.
		"""
		
		state = {
			"platforms": {}
		}
		for name, stub in self.__platform_stubs.items():
			state["platforms"][name] = {
				"provider": stub.provider(),
				"properties": stub.properties()
			}
		state_file = self.__state_res.open("w")
		jsons.write_dict(state_file, state, True)
		state_file.write("\n")
		state_file.close()

