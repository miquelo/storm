Platform interfaces
===================

Interfaces for implementing platform provider.

.. class:: Platform(data_res, props)

   Platform main interface.
   
   :param Resource data_res:
      Resource holding platform data.
   :param props:
      Optional properties.
   
   .. function:: destroy(context)
   
      Destroy the platform.
      
      :param PlatformTaskContext context:
         Current platform task context.
         
.. class:: PlatformTaskContext

   Execution context of a platform task.
   
   .. function:: message(value)
   
      Dispatch an engine task message event.
      
      :param value:
         Message value.
         
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
         
   .. function:: work_start(desc)
   
      Start a new platform task work.
      
      :param string desc:
         Work description.
      :rtype:
         PlatformTaskWork
      :return:
         The started task work.
         
.. class:: PlatformTaskWork

   Individual work of platform task.
   
   .. function:: progress(value)
   
      Dispatch a work progress event.
      
      :param float value:
         Progress value.
         
   .. function:: finished()
   
      Mark this work as finished.

