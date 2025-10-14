.. _using-datamodels:

Using Roman Datamodels
======================

.. note::
   IPython and jupyter won't automatically tab-complete the
   dynamic attributes of datamodels. To enable tab-completion
   add the following to your `ipython configuration <https://ipython.readthedocs.io/en/stable/config/intro.html>`_::

       c.IPCompleter.evaluation = "unsafe"
       c.IPCompleter.use_jedi = False

The following illustrates common operations with the datamodels.
This is most relevant for interactive use with a loaded datamodel
or if one is writing scripts or programs to view and manipulate
these data models. Developing new datamodels is a different topic
and may be covered in the future. For the most part, it involves
defining what the schema for such a model must be and what modifications
are needed to the code to support it (usually not much).

The normal approach is to open the datamodel as follows (this assumes
the file displayed as the Level 1 example in the general structure
page::

    >>> import roman_datamodels as rdm
    >>> dm = rdm.open('my_wonderful_roman_data.asdf')

    >>> type(dm)
    <class 'roman_datamodels.datamodels._datamodels.ScienceRawModel'>

    # Can view the associated schema
    >>> dm.schema_uri
    'asdf://stsci.edu/datamodels/roman/schemas/wfi_science_raw-1.0.0'

    >>> print(dm.meta.instrument.optical_element)
    GRISM

    # Most nodes have special types

    >>> type(dm.meta.exposure)
    roman_datamodels.stnode.Exposure

    >>> print(dm.data.shape)
    (8, 4096, 4096)

    >>> print(dm.data.dtype)
    uint16

    # Change metadata value

    >>> dm.meta.exposure.exposure_time = 60000.
    >>> print(dm.meta.exposure.exposure_time)
    60000.0

    # Assign invalid type

    >>> dm.meta.exposure.exposure_time = "hello"
    >>> dm.validate()

    # Last part of resulting traceback

    ValidationError: While validating exposure_time the following error occurred:
    'hello' is not of type 'number'

    Failed validating 'type' in schema:
        {'$schema': 'http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema',
         'archive_catalog': {'datatype': 'float',
                             'destination': ['WFIExposure.exposure_time',
                                             'GuideWindow.exposure_time',
                                             'WFICommon.exposure_time']},
         'description': 'The difference in time (in units of seconds) between\n'
                        'the start of the first reset/read and end of the last '
                        'read in\n'
                        'the readout pattern.\n',
         'sdf': {'source': {'origin': 'TBD'},
                 'special_processing': 'VALUE_REQUIRED'},
         'title': 'Exposure Time (s)',
         'type': 'number'}

    On instance:
        'hello'

    # Note the extra information in the schema segment showing origin of
    # the information and the destination in the archive.

    # Try to assign wrong kind of node

    >>> dm.meta.observation = dm.meta.exposure
    >>> dm.validate()

    Failed validating 'tag' in schema:
        {'$schema': 'http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema',
         'tag': 'asdf://stsci.edu/datamodels/roman/tags/observation-1.0.0',
         'title': 'Observation Identifiers'}

    On instance:
        {'data_problem': False,
         'effective_exposure_time': -999999,
         'end_time': '2020-01-01T02:00:00.000',
         'exposure_time': 60000.0,
         'frame_time': -999999,
         'ma_table_name': '?',
         'ma_table_number': -999999,
         'mid_time': '2020-01-01T01:00:00.000',
         'nresultants': 6,
         'read_pattern': [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]],
         'start_time': '2020-01-01T00:00:00.000',
         'truncated': False,
         'type': 'WFI_IMAGE'}

    # Show and then change pixel value in data

    >>> dm.data[0, 10, 10]
    115
    >>> dm.data[0, 10, 10] = 42
    >>> dm.data[0, 10, 10]
    42

    # Save to a new file

    >>> dm.to_asdf('test.asdf')
    >>> dm2 = rdm.open('test.asdf')
    >>> dm2.data[0, 10, 10]
    42
    >>> dm2.meta.exposure.exposure_time
    60000.0
