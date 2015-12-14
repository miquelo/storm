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
   
   .. function:: dispatch(name, value=None)
   
      Dispatch an engine task event.
      
      :param string name:
         Event name.
      :param value:
         Event value.
   
   .. function:: out()
   
      Return the engine output stream.
      
      :return:
         The engine output stream.
         
   .. function:: err()
   
      Return the engine error stream.
      
      :return:
         The engine error stream.
         
   .. function:: cancel_check()
   
      Check if caller engine task was cancelled.
      
      :raises storm.engine.EngineTaskCancelled:
         If it was already cancelled.

