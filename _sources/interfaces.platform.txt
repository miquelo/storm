Platform interfaces
===================

Interfaces for implementing platform provider.

.. class:: Platform

   Platform main interface.
   
   .. function:: configure(context, props=None)
   
      Creates a task for configuring this platform with the given properties.
      
      :param PlatformTaskContext context:
         Current platform task context.
      :param props:
         Dictionary with the configuration properties.
         
.. class:: PlatformTaskContext

   Execution context of a platform task.
   
   .. function:: message(msg)
   
      Sends a message to the engine event queue.
      
      :param msg:
         Message to be sent.
         
   .. function:: cancel_check()
   
      Check if caller engine task was cancelled.
      
      :raises storm.engine.EngineTaskCancelled:
         If it was already cancelled.

