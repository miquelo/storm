Engine interfaces
=================

Interfaces related with the engine.
   
.. class:: EngineTask

   Scheduled task for engine operations.

   .. function:: result(timeout)
   
.. class:: EngineTaskEvent

   Event fired by an engine task.
   
   .. attribute:: task

      Event source of type :class:`EngineTask`.
      
   .. attribute:: name
   
      Type name of this event.
      
   .. attribute:: value
   
      Value of this event.
   
.. function:: engine_dispatch_event_fn(event)

   Function used for task event dispatching.
   
   :param EngineTaskEvent event:
      Event to be dispatched.

