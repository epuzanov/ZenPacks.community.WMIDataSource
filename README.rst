================================
ZenPacks.community.WMIDataSource
================================

DEPRECATION WARNING
===================

Use of WMI data source is deprecated. Please use
`SQL <http://community.zenoss.org/docs/DOC-5913>`_ data source with **pywmidb**
DB-API 2.0 interface instead.

About
=====

This Functionality ZenPack provides a new **WMI** data source and **zWmiProxy** 
zProperty.


Requirements
============

Zenoss
------

You must first have, or install, Zenoss 2.5.2 or later. This ZenPack was tested 
against Zenoss 2.5.2 and Zenoss 3.2. You can download the free Core version of 
Zenoss from http://community.zenoss.org/community/download

ZenPacks
--------

You must first install `SQLDataSource ZenPack <http://community.zenoss.org/docs/DOC-5913>`_.


Installation
============

Normal Installation (packaged egg)
----------------------------------

Download the `WMIDataSource ZenPack <http://community.zenoss.org/docs/DOC-3392>`_. 
Copy this file to your Zenoss server and run the following commands as the zenoss 
user.

    ::

        zenpack --install ZenPacks.community.WMIDataSource-3.0.egg
        zenoss restart

Developer Installation (link mode)
----------------------------------

If you wish to further develop and possibly contribute back to the WMIDataSource 
ZenPack you should clone the git `repository <https://github.com/epuzanov/ZenPacks.community.WMIDataSource>`_, 
then install the ZenPack in developer mode using the following commands.

    ::

        git clone git://github.com/epuzanov/ZenPacks.community.WMIDataSource.git
        zenpack --link --install ZenPacks.community.WMIDataSource
        zenoss restart


Usage
=====

Query syntax
------------

enumerate all Instances of CIM_Processor class example:

    ::

        CIM_Processor

enumerate all Instances of CIM_Processor class, WQL syntax example:

    ::

        SELECT * FROM CIM_Processor

get single Instance for CPU0 example:

    ::

        CIM_Processor.DeviceID="CPU0"

get single Instance for CPU0, WQL syntax example:

    ::

        SELECT * FROM CIM_Processor WHERE DeviceID="CPU0"

get single Instance from specific namespace:

    ::

        root/cimv2:CIM_Processor.DeviceID="CPU0"


Columns name to Data Points name mapping
----------------------------------------
use SQL Aliases Syntax for columns names to set the same name as Data Poins 
names.

Example query which returned values for **LoadPercentage** and 
**OperationalStatus** Data Points:

    ::

        SELECT LoadPercentage,OperationalStatus FROM CIM_Processor

Queue sorting (join multiple queries in single query)
-----------------------------------------------------
WHERE statement will be removed from SQL Query and used as key by results parsing.

Example:
We have 4 Processors and we need collect **LoadPercentage** values for each one.

DataSource Query for **LoadPercentage** of **CPU0**:

    ::

        SELECT LoadPercentage FROM CIM_Processor WHERE DeviceID="CPU0"

DataSource Query for **LoadPercentage** of **CPU1**:

    ::

        SELECT LoadPercentage FROM CIM_Processor WHERE DeviceID="CPU1"

DataSource Query for **LoadPercentage** of **CPU2**:

    ::

        SELECT LoadPercentage FROM CIM_Processor WHERE DeviceID="CPU2"

DataSource Query for **LoadPercentage** of **CPU3**:

    ::

        SELECT LoadPercentage FROM CIM_Processor WHERE DeviceID="CPU3"

As result 4 queries will be replaced by single query:

    ::

        SELECT LoadPercentage FROM CIM_Processor

Data Point Aliases formulas
---------------------------
before be saved in RRD, values will be evaluated by **REVERSED** alias.formula

- supported operations: **+, -, *, /**
- tales variables: now, here

Example:

alias.formula = **"100,/,1,-"** replaced by **REVERSED** formula **"1,+,100,*"**

Why alias.formula must be reversed?

- raw data: **100** -> **"100,100,/,1,-"** -> RRD: **0** -> **"0,100,/,1,-"** ->Report: **-1** - FALSE!
- raw data: **100** -> **"100,1,+,100,*"** -> RRD: **10100** -> **"10100,100,/,1,-"** ->Report: **100** - TRUE!

Dictionary as Data Point Aliases formula
----------------------------------------
before be saved in RRD, values will be evaluated

Example:

    ::

        "Unknown":0,"Other":1,"OK":2,"Warning":3,"Error":4

Agregation functions support for multiline results
--------------------------------------------------
Agregation functions **avg**, **count**, **sum**, **min**, **max**, **first**, 
**last** are supported for data points with multiline result. If query returned 
multiple values for single Data Point, than zenperfsql datemon used **avg** 
function by default. If another function must be used, than add **_function** 
to the data points name.

Example:

- **LoadPercentage_max** - will write in to RRD file maximal **LoadPercentage** value
