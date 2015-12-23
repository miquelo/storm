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
				
					self.__worker.message(value)
					
				def progress(self, value):
				
					self.__worker.progress(value)
					
				def out(self):
				
					return self.__worker.out()
					
				def err(self):
				
					return self.__worker.err()
					
				def cancel_check(self):
				
					return self.__worker.cancel_check()
					
			self.__event_queue = event_queue
			self.__task_fn = task_fn
			self.__out = out
			self.__err = err
			self.__context = PlatformTaskContext(self)
			self.__future = None
			self.__engine_task = None
			self.__cancel_check = self.__cancel_check_pass
			self.__progress_val = 0.
			self.__progress_track = 0.
				
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
			
		def progress_track(self, track):
		
			self.__progress_val = self.__progress_val + self.__progress_track
			self.__progress_track = track
			self.progress(0.)
			
		def dispatch(self, name, value=None):
		
			self.__event_queue.dispatch(self.__engine_task, name, value)
			
		def message(self, value):
		
			self.dispatch("message", value)
			
		def progress(self, value):
		
			if value is None:
				pval = None
			else:
				pval = self.__progress_val + self.__progress_track * value
			self.dispatch("progress", pval)
			
	def __init__(
		self,
		state_res,
		event_queue=None,
		out=None,
		err=None
	):
	
		def resolvable(obj, props):
		
			def resolvable_result(obj):
			
				if isinstance(obj, list):
					return ResolvableList(obj)
				if isinstance(obj, dict):
					return ResolvableDict(obj)
				if isinstance(obj, str):
					r_in = io.StringIO(obj)
					r_out = io.StringIO()
					resolver.resolve(r_in, r_out, props)
					r_out.seek(0)
					return r_out.read()
				return obj
				
			class ResolvableList(list):
			
				def __init__(self, obj):
				
					self.extend(obj)
					
				def __getitem__(self, key):
				
					return resolvable_result(super().__getitem__(key))
					
				def __iter__(self):
				
					return ResolvableListIterator(super().__iter__())
					
				def __reversed__(self):
				
					return ResolvableListIterator(super().__reversed__())
					
			class ResolvableListIterator:
			
				def __init__(self, it):
				
					self.__it = it
					
				def __iter__(self):
				
					return self
					
				def __next__(self):
				
					return resolvable_result(self.__it.__next__())
					
			class ResolvableDict(dict):
			
				def __init__(self, obj):
				
					self.update(obj)
					
				def __getitem__(self, key):
				
					return resolvable_result(super().__getitem__(key))
					
				def __iter__(self):
				
					return ResolvableDictIterator(super().__iter__())
					
				def __reversed__(self):
				
					return ResolvableDictIterator(super().__reversed__())
					
				def items(self):
				
					return [
						(key, resolvable_result(value))
						for key, value in super().items()
					]
					
			class ResolvableDictIterator:
			
				def __init__(self, it):
				
					self.__it = it
					
				def __iter__(self):
				
					return self
					
				def __next__(self):
				
					return self.__it.__next__()
					
			return resolvable_result(obj)
			
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
					rprops = resolvable(self.__props, self.__props)
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
				
			def configure(self, context):
			
				return self.__platform().configure(context)
				
			def destroy(self, context):
			
				return self.__platform().destroy(context)
				
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
					self.__platform_stubs.put(
						name,
						self.__platform_stubs.create(
							name,
							prov,
							props,
							state_res
						)
					)
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
	
		plat_stubs_len = len(self.__platform_stubs)
		
		if plat_stubs_len == 0:
			worker.progress_track(1.)
			worker.progress(1.)
		else:
			ptrack = 1. / plat_stubs_len
			worker.progress_track(ptrack)
			for name, stub in self.__platform_stubs.items():
				worker.cancel_check()
				worker.dispatch("platform-entry", {
					"name": name,
					"available": stub.available(),
					"provider": stub.provider()
				});
				worker.progress_track(ptrack)
				
		return plat_stubs_len
		
	def __register(self, worker, name, prov, props):
	
		state_res = self.__state_res
		stub = self.__platform_stubs.create(name, prov, props, state_res)
		worker.progress_track(1.)
		stub.configure(worker.context())
		self.__platform_stubs.put(name, stub)
		
	def __dismiss(self, worker, name, destroy):
	
		worker.progress_track(1.)
		if destroy:
			stub = self.__platform_stubs.get(name)
			stub.destroy(worker.context())
		else:
			worker.progress(1.)
		stub = self.__platform_stubs.remove(name)
			
	def __watch(self, worker, name):
	
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

