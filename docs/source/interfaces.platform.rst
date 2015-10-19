Platform interfaces
===================

Interfaces for implementing platform provider.

.. class:: Platform

   Platform main interface.
   
   .. function:: configure(props=None)
   
      Creates a task for configuring this platform with the given properties.
      
      :param props:
         Dictionary with the configuration properties.
      :rtype:
         PlatformTask
      :return:
         The created task.
         
.. class:: PlatformTask

   Task done by a platform.
   
   .. function:: run(context)
   
      Run this task.
      
      :param PlatformTaskContext context:
         Execution context.
         
      :return:
         The result value.
         
   .. function:: cancel()
   
      Cancel this task. It can be done in another thread.
      
      :rtype:
         bool
      :return:
         True if cancellation was succesfully done. False otherwise.
      
.. class:: PlatformTaskContext

   Execution context of a platform task.

