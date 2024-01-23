.. _index:

Overview
========

Welcome to the Mazure documentation!
------------------------------------

**Mazure** is a proxy that mocks the Azure SDK.

Using a mocked Azure will:
 - Save you time, as you no longer have to wait for long-running HTTP-requests to Azure
 - Save you time, as you no longer have to write your own mocks
 - Save you money, as you no longer have to create resources in Azure (and no longer have to remember to delete them after every test!)
 - Gain you confidence that you're using the Azure SDK correctly

Usage
-----

1. Run the Mazure Docker image:

```
docker run -p 5005:5005 mazureproxy/proxy:0.0.2
```

2. Configure the SDK of your choice to  use the proxy:

:doc:`sdk_specific_config`.


Supported Services
------------------

Please see our :doc:`list of supported services here <supported_services>`.

Want to see support for another service? Let us know!


.. toctree::
   :maxdepth: 1
   :hidden:

   self
   sdk_specific_config
   supported_services
