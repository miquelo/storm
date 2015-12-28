Module interfaces
=================

.. class:: ProcessContext

   Context of an external process execution.
   
   .. function:: working_dir()
   
      Process working directory.
      
   .. function:: out()
   
      Output stream.
      
   .. function:: err()
   
      Error stream.
      
   .. function:: cancel_check()
   
      Check if process execution was cancelled.
      
      :raises storm.module.util.ProcessCancelled:
         If it was already cancelled.

