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
from storm.module import resolver
from storm.module import resource

import concurrent.futures
import importlib
import threading

class Engine:

	"""
	The engine of the management tool.
	
	:param Resource state_res:
	   Resource holding the state of the engine.
	:param EngineEventQueue event_queue:
	   Event queue used for dispatching engine task events.
	:param out:
	   Output stream.
	:param err:
	   Error stream.
	"""
	
	class __EngineTaskWorker:
	
		def __init__(self, event_queue, task_fn, out, err):
		
			class PlatformTaskContext:
			
				def __init__(self, worker):
				
					self.__worker = worker
					
				def message(self, value):
				
					self.__worker.dispatch("message", value)
					
				def out(self):
				
					return self.__worker.out()
					
				def err(self):
				
					return self.__worker.err()
					
				def cancel_check(self):
				
					return self.__worker.cancel_check()
					
				def work_start(self, desc):
				
					return self.__worker.work_start(desc)
					
			self.__event_queue = event_queue
			self.__task_fn = task_fn
			self.__out = out
			self.__err = err
			self.__context = PlatformTaskContext(self)
			self.__work_id = 0
			self.__work_id_lock = threading.Lock()
			self.__future = None
			self.__engine_task = None
			self.__cancel_check = self.__cancel_check_pass
				
		def __task_run(self, *args, **kwargs):
		
			try:
				self.dispatch("started")
				result = self.__task_fn(self, *args, **kwargs)
				return result
			finally:
				self.dispatch("finished")
			
		def __cancel_check_pass(self):
		
			pass
			
		def __cancel_check_raise(self):
		
			self.__cancel_check = self.__cancel_check_pass
			raise EngineTaskCancelled()
			
		def context(self):
		
			return self.__context
			
		def work_start(self, desc):
		
			return self.__context.work_start(desc)
			
		def new_work_id(self):
		
			try:
				self.__work_id_lock.acquire()
				return self.__work_id
			finally:
				self.__work_id = self.__work_id + 1
				self.__worl_id_lock.release()
			
		def submit(self, executor, args, kwargs):
		
			class EngineTask:
			
				def __init__(self, worker):
				
					self.__worker = worker
				
				def result(self, timeout=None):
				
					return self.__worker.result(timeout)
				
				def cancel(self):
				
					return self.__worker.cancel()
					
			self.__engine_task = EngineTask(self)
			self.__future = executor.submit(self.__task_run, *args, **kwargs)
			return self.__engine_task
			
		def result(self, timeout):
		
			return self.__future.result(timeout)
			
		def cancel(self):
		
			cancelled = self.__future.cancel()
			self.__cancel_check = self.__cancel_check_raise
			return cancelled
				
		def out(self):
		
			return self.__out
			
		def err(self):
		
			return self.__err
			
		def cancel_check(self):
		
			self.__cancel_check()
			
		def work_start(self, desc):
		
			class PlatformTaskWork:
			
				def __init__(self, worker, desc, parent_id=None):
				
					self.__worker = worker
					self.__work_id = self.__worker.new_work_id()
					self.__progress = 0.
					
					self.__dispatch("started", {
						"description": desc,
						"parent-id": parent_id
					})
					
				def __dispatch(self, cause, value=None):
				
					self.__worker.dispatch("work", {
						"id": self.__work_id,
						"cause": cause,
						"value": value
					})
					
				def context(self):
				
					return self.__worker.context()
					
				def progress(self, amount, desc=None):
				
					self.__progress = self.__progress + amount
					self.__dispatch("progress", {
						"description": desc,
						"value": self.__progress
					})
					
				def finished(self):
				
					self.__dispatch("finished")
					
				def work_start(self, desc, cost):
				
					return PlatformTaskWorkChild(
						self.__worker,
						desc,
						self.__work_id,
						self,
						cost
					)
					
			class PlatformTaskWorkChild(PlatformTaskWork):
			
				def __init__(self, worker, desc, parent_id, parent, cost):
				
					super().__init__(worker, desc, parent_id)
					self.__parent = parent
					self.__cost = cost
					
				def progress(self, amount, desc=None):
				
					self.__parent.progress(self.__cost * amount)
					super().progress(amount, desc)
					
			return PlatformTaskWork(self, desc)
			
		def dispatch(self, name, value=None):
		
			self.__event_queue.dispatch(self.__engine_task, name, value)
			
	def __init__(
		self,
		state_res,
		event_queue=None,
		out=None,
		err=None
	):
	
		class IgnoreEventQueue():
		
			def dispatch(self, task, name, value):
			
				pass
				
		class NoneOutput:
		
			def write(self, text):
			
				pass
				
		class PlatformStubs:
		
			def __init__(self):
			
				self.__stubs = {}
				self.__access_lock = threading.Lock()
				
			def __len__(self):
			
				try:
					self.__access_lock.acquire()
					return len(self.__stubs)
				finally:
					self.__access_lock.release()
					
			def create(self, name, prov, props, state_res):
			
				data_res = state_res.parent().ref("platforms").ref(name)
				return PlatformStub(prov, data_res, props)
				
			def items(self):
			
				try:
					self.__access_lock.acquire()
					yield from self.__stubs.items()
				finally:
					self.__access_lock.release()
					
			def get(self, name):
			
				try:
					self.__access_lock.acquire()
					return self.__stubs[name]
				except KeyError:
					raise Exception("Platform '{}' does not exist".format(name))
				finally:
					self.__access_lock.release()
					
			def put(self, name, stub):
			
				try:
					self.__access_lock.acquire()
					if name in self.__stubs:
						msg = "Platform '{}' already exists".format(name)
						raise Exception(msg)
					self.__stubs[name] = stub
				finally:
					self.__access_lock.release()
					
			def remove(self, name):
			
				try:
					self.__access_lock.acquire()
					del self.__stubs[name]
				except KeyError:
					raise Exception("Platform '{}' does not exist".format(name))
				finally:
					self.__access_lock.release()
					
		class PlatformStub:
		
			def __init__(self, prov, data_res, props):
			
				self.__prov = prov
				self.__props = props
				
				try:
					mod_name = "storm.provider.platform.{}".format(self.__prov)
					mod = importlib.import_module(mod_name)
					rprops = resolver.resolvable(self.__props, self.__props)
					self.__plat = mod.Platform(data_res, rprops)
				except ImportError:
					self.__plat = None
					
			def __platform(self):
			
				if not self.available():
					msg = "Platform with provider '{}'".format(self.__prov)
					msg = "{} is not available".format(msg)
					raise LookupError(msg)
				return self.__plat
				
			def available(self):
			
				return self.__plat is not None
				
			def provider(self):
			
				return self.__prov
				
			def properties(self):
			
				return self.__props
				
			def builder(self):
			
				return self.__platform().builder()
				
			def repository(self):
			
				return self.__platform().repository()
				
			def executor(self):
			
				return self.__platform().executor()
				
			def destroy(self, work):
			
				return self.__platform().destroy(work)
				
		self.__state_res = state_res
		self.__event_queue = event_queue or IgnoreEventQueue()
		self.__out = out or NoneOutput()
		self.__err = err or NoneOutput()
		self.__executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
		self.__platform_stubs = PlatformStubs()
		
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
					stub = self.__platform_stubs.create(
						name,
						prov,
						props,
						state_res
					)
					self.__platform_stubs.put(name, stub)
		except resource.ResourceNotFoundError:
			pass
			
	def __engine_task(self, task_fn, *args, **kwargs):
	
		worker = self.__EngineTaskWorker(
			self.__event_queue,
			task_fn,
			self.__out,
			self.__err
		)
		return worker.submit(self.__executor, args, kwargs)
		
	def __platforms(self, worker):
	
		for name, stub in self.__platform_stubs.items():
			worker.cancel_check()
			worker.dispatch("platform-entry", {
				"name": name,
				"available": stub.available(),
				"provider": stub.provider()
			});
		return len(self.__platform_stubs)
		
	def __register(self, worker, name, prov, props):
	
		state_res = self.__state_res
		stub = self.__platform_stubs.create(name, prov, props, state_res)
		self.__platform_stubs.put(name, stub)
		
	def __dismiss(self, worker, name, destroy):
	
		if destroy:
			stub = self.__platform_stubs.get(name)
			work = worker.work_start("Destroying '{}' platform".format(name))
			stub.destroy(work)
			work.finished()
		stub = self.__platform_stubs.remove(name)
			
	def __watch(self, worker, name):
	
		stub = self.__platform_stubs.get(name)
		work = worker.work_start("Retrieving '{}' platform state".format(name))
		return None
		
	def __offer(self, worker, name, image):
	
		pass
		
	def __retire(self, worker, name, image):
	
		pass
		
	def __emerge(self, worker, layout):
	
		pass
		
	def platforms(self):
	
		"""
		Returns a dictionary containing name/provider entries.
		
		:rtype:
		   EngineTask
		:return:
		   The task running the platforms process.
		"""
		
		return self.__engine_task(self.__platforms)
		
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
		
		return self.__engine_task(self.__register, name, prov, props)
		
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
		
		return self.__engine_task(self.__dismiss, name, destroy)
		
	def watch(self, name):
	
		"""
		Requests the state of some platform.
		
		:param string name:
		   The name of the platform that will give its state.
		:rtype:
		   EngineTask
		:return:
		   The task running the watch process.
		:raises Exception:
		   If the platform with the given name does not exist.
		"""
		
		return self.__engine_task(self.__watch, name)
		
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
		
		return self.__engine_task(self.__offer, name, image)
		
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
		
		return self.__engine_task(self.__retire, name, image)
		
	def emerge(self, layout):
	
		"""
		Try to do layout to be in the given state accross platforms.
		
		:param storm.engine.layout.Layout layout:
		   The layout to be put into construction.
		:rtype:
		   EngineTask
		:return:
		   The task running the emerge process.
		"""
		
		return self.__engine_task(self.__emerge, layout)
		
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
		
class EngineTaskCancelled(Exception):

	"""
	Engine task cancellation.
	"""
	
	def __init__(self):
	
		super().__init__(None)

