Available commands
==================

Its commands are intimately bound with :class:`storm.engine.Engine` class.

For each command, the main process is the same. First of all, creates an engine
using the file ``APP_DATA_DIR/engine.json`` as state resource. Then schedules
the associated task for executing. Remains listening for engine events still
"finished" event is fired. And, at the end, collects result and use it as
output. Its final state is stored in the state resource.

Listing platforms
-----------------

Prints the list of registered platforms. Each entry has the name of the
platform and the name of its provider.

The next example represents an engine with five registered platforms. Two,
*local1* and *local2* of the provider *devel*. One of the provider *azure*
named *pre*. Another one named *pro-up*, of the provider *mixed*. And one of
provider *aws* named *pro-fb*.

.. code:: bash

   $ storm platforms
     local1 devel
     local2 devel
     pre azure
     pro-up mixed
     pro-fb aws

Registering some platform
-------------------------

Register a platform with the given name using the specified platform provider.
Optional properties can be given by specifying properties resources.

For example,

.. code:: bash

   $ storm register pre azure pre-config.json company-values.json
   
registers a platform named *pre* of the provider *azure*. Files
*pre-config.json* and *company-values.json* are parsed as JSON objects, merged
and passed as register operation properties.

Dismissing some platform
------------------------

Watching some platform
----------------------

Offering an image to some platform
----------------------------------

Retiring an image from some platform
------------------------------------

Emerging some layout
--------------------

