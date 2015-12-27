Platform interfaces
===================

Interfaces for implementing platform provider.

.. class:: Platform(base_res, props)

   Platform main interface.
   
   :param Resource base_res:
      Resource holding platform data.
   :param props:
      Optional properties.
      
   .. function:: builder()
   
      Return the platform image builder.
      
      :rtype:
         ImageBuilder
      :return:
         The platform image builder.
         
   .. function:: repository()
   
      Return the platform image repository.
      
      :rtype:
         ImageRepository
      :return:
         The platform image repository.
         
   .. function:: executor()
   
      Return the platform container executor.
      
      :rtype:
         ContainerExecutor
      :return:
         The platform container executor.
         
   .. function:: destroy(work)
   
      Destroy the platform.
      
      :param PlatformTaskWork work:
         Current platform task work.
         
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
      
      Dispatch a work started event.
      
      :param string desc:
         Work description.
      :rtype:
         PlatformTaskWork
      :return:
         The started task work.
         
.. class:: PlatformTaskWork

   Individual work of platform task.
   
   .. function:: context()
   
      Return the current platform task context.
      
      :rtype:
         PlatformTaskContext
      :return:
         Current context.
         
   .. function:: progress(amount, desc=None)
   
      Dispatch a work progress event with adding the given amount.
      
      :param float amount:
         Progress amount to be added.
      :param string desc:
         Progress description.
         
   .. function:: finished()
   
      Dispatch a work finisehed event.
      
   .. function:: work_start(desc, cost)
   
      Start a new platform task subwork.
      
      Dispatch a work started event.
      
      :param string desc:
         Work description.
      :param float cost:
         Cost of this work.
      :rtype:
         PlatformTaskWork
      :return:
         The started task work.
         
.. class:: ImageBuilder

   Container image builder.
   
   .. function:: build(work, image)
   
      Build the given image.
      
      :param PlatformTaskWork work:
         Current platform task work.
      :param storm.engine.image.Image image:
         Image to be built.
      :rtype:
         storm.engine.image.ImageRef
      :return:
         The reference of the built image.
         
.. class:: ImageRepository

   Container image repository.
   
   .. function:: publish(work, image_ref)
   
      Publish the image with the given reference.
      
      :param PlatformTaskWork work:
         Current platform task work.
      :param storm.engine.image.ImageRef image_ref:
         Reference of the image to be published.
         
.. class:: ContainerExecutor

   Container executor.
   
   .. function:: setup(work, cont, config)
   
      Execute a container.
      
      :param PlatformTaskWork work:
         Current platform task work.
      :param storm.engine.layout.Container cont:
         Container to be executed.
      :param storm.engine.layout.ContainerSetupConfig config:
         Setup configuration.

