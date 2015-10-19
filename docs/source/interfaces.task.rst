Task interfaces
===============

Interfaces used for task execution.

.. class:: TaskExecutor

   Executor for tasks.
   
   Implemented by:
   
   - :class:`concurrent.futures.Executor`
   
   .. function:: submit(task_fn, *args, *kwargs)
   
      Schedules a task.
      
      :param executor_task_fn task_fn:
         Task function to be executed.
      :param args:
         Optional positional arguments.
      :param kwargs:
         Optional keyword arguments.
      :rtype:
         TaskFuture
      :return:
         The future object associated to the scheduled task.
         
.. class:: TaskFuture

   Future object associated to a task.
   
   Implemented by:
   
   - :class:`concurrent.futures.Future`
   
   .. function:: result(timeout)
   
.. function:: executor_task_fn(*args, **kwargs)

   :param args:
      Optional positional arguments.
   :param kwargs:
      Optional keyword arguments.

