Resource interfaces
===================

Interfaces for resource management.

.. class:: Resource

   Protocol agnostic resource.
   
   .. attribute:: scheme
   
      Scheme of the resource URI.
      
   .. attribute:: location
   
      Location of the resource URI of type :class:`ResourceLocation`.
      
   .. attribute:: path
   
      Path of the resource URI.
      
   .. attribute:: query
   
      Query of the resource URI.
      
   .. attribute:: fragment
   
      Fragment of the resource URI.
      
   .. function:: unref()
   
      Returns the URI representation of this resource.
      
      :rtype: string
      
   .. function:: ref(path, query=None, fragment=None)
   
      Returns a new resource referencing the given path relative to this
      resource path.
      
      The new resource will have the same scheme and location than this
      resource.
      
      :param string path:
         Relative path.
      :param string query:
         Optional query part.
      :param string fragment:
         Optional fragment part.
      :rtype:
         Resource
      
   .. function:: parent(query=None, fragment=None)
   
      Returns a new resource referencing the parent path relative to this
      resource path.
      
      The new resource will have the same scheme and location than this
      resource.
      
      :param string query:
         Optional query part.
      :param string fragment:
         Optional fragment part.
      :rtype: Resource
      
   .. function:: exists()
   
      Checks if this resource already exists.
      
      :rtype:
         bool
      :return:
         True if this resource exists. False otherwise.
         
   .. function:: name()
   
      Returns the base name of this resource.
      
      :rtype:
         string
         
   .. function:: delete()
   
      Delete this resource.
      
      :rtype:
         bool
      :return:
         True if this resource was succesfully deleted. False otherwise.
         
   .. function:: open(flags)
   
      Open this resource and returns its associated stream.
      
      :param flags:
         Open flags.
      :rtype:
         ResourceStream
      :return:
         The associated stream.
      :raises storm.module.resource.ResourceNotFoundError:
         If resource existence is needed but not honored.
         
.. class:: ResourceLocation

   Location of a resource.
   
   .. function:: __str__()
   
      Literal representation.
      
   .. attribute:: username
   
      Location user name.
      
   .. attribute:: password
   
      Location password.
      
   .. attribute:: hostname
   
      Location host name.
      
   .. attribute:: port
   
      Location integer value port.
      
.. class:: ResourceStream

   This is like a :class:`fileobj`.
   
.. class:: ResourceHandler

   Protocol dependent resource handler.
   
   .. function:: exists()
   
      Checks if this resource already exists.
      
      :rtype:
         bool
      :return:
         True if this resource exists. False otherwise.
         
   .. function:: name()
   
      Returns the base name of this resource.
      
      :rtype:
         string
         
   .. function:: delete()
   
      Delete this resource.
      
      :rtype:
         bool
      :return:
         True if this resource was succesfully deleted. False otherwise.
         
   .. function:: open(flags)
   
      Open this resource and returns its associated stream.
      
      :param flags:
         Open flags.
      :rtype:
         ResourceStream
      :return:
         The associated stream.
      :raises storm.module.resource.ResourceNotFoundError:
         If resource existence is needed but not honored.
         
.. function:: resource_isabs(path)

   Checks if the given path is an absolute path.
   
   :param string path:
      The path to be checked.
   :rtype:
      bool
   :return:
      True if the given path is an absolute path. False otherwise.
      
.. function:: resource_abspath(path)

.. function:: resource_dirname(path)

.. function:: resource_join(base_path, relative_path)

