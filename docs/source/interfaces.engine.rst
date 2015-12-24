Engine interfaces
=================

Interfaces related with the engine.
   
.. class:: EngineTask

   Scheduled task for engine operations.
   
   .. function:: result(timeout)
   
.. class:: EngineEventQueue

   Queue for engine task events.
   
   .. function:: dispatch(task, name, value)
   
      Function used for task event dispatching.
      
      :param EngineTask task:
         Source task.
      :param string name:
         Event type name.
      :param value:
         Event value.
         
.. class:: ImageResource

   Container image resource.
   
   .. attribute:: source_res
   
      Source :class:`Resource`.
      
   .. attribute:: target_res
   
      Target :class:`Resource`.
      
   .. attribute:: properties
   
      Resource properties.
      
.. class:: ImageCommand

   Container image command.
   
   .. attribute:: arguments
   
      Command arguments.

