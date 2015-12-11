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
   
   .. function:: write_out(text)
   
      Write text to the output stream.
      
      :param string text:
         Text to be written.
      :rtype:
         int
      :return:
         The number of written characters.
         
   .. function:: write_err(text)
   
      Write text to the error stream.
      
      :param string text:
         Text to be written.
      :rtype:
         int
      :return:
         The number of written characters.
         
   .. function:: cancel_check()
   
      Check if caller engine task was cancelled.
      
      :raises storm.engine.EngineTaskCancelled:
         If it was already cancelled.

