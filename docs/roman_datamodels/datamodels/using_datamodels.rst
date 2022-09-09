Using Roman Datamodels
======================

The following illustrates common operations with the datamodels.
This is most relevant for interactive use with a loaded datamodel
or if one is writing scripts or propgrams to view and manipulate
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
	roman_datamodels.datamodels.ScienceRawModel

	>>> print(dm.meta.instrument.optical_element)
	GRISM

	# most nodes have special types

	>>> type(dm.meta.exposure)
	roman_datamodels.stnode.Exposure

	>>> print(dm.data.shape)
	(6, 4096, 4096)

	>>> print(dm.data.dtype)
	uint16

	# Change metadata value

	>>> dm.meta.exposure.start_time_mjd = 60000.
	print(dm.meta.exposure.start_time_mjd)
	60000.0

	# Try to assign invalid type

	>>> d.meta.exposure.start_time_mjd = "hello"

	# Last part of resulting traceback

	ValidationError: While validating start_time_mjd the following error occurred:
	'hello' is not of type 'number'

	Failed validating 'type' in schema:
	    {'$schema': 'http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema',
	     'archive_catalog': {'datatype': 'float',
	                         'destination': ['ScienceCommon.exposure_start_time_mjd']},
	     'description': 'This records the time at the start of the exposure '
	                    'using the\n'
	                    'Modified Julian Date (MJD). This is used in the '
	                    'archive catalog for\n'
	                    'multi-mission matching.\n',
	     'sdf': {'source': {'origin': 'TBD'},
	             'special_processing': 'VALUE_REQUIRED'},
	     'title': '[d] exposure start time in MJD',
	     'type': 'number'}

	On instance:
	    'hello'

	# Note the extra information in the schema segment showing origin of
	# the information and the destination in the archive.

	# Try to assign wrong kind of node

	>>> dm.meta.observation = dm.meta.exposure
	Failed validating 'tag' in schema:
	    {'$schema': 'http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema',
	     'tag': 'asdf://stsci.edu/datamodels/roman/tags/observation-1.0.0'}

	On instance:
	    {'groupgap': 0, 'ma_table_name': 'High Latitude Spec. Survey', 'ma_table_number': 1, 'nframes': 8, 'ngroups': 6, 'p_exptype': 'WFI_IMAGE|', 'type': 'WFI_IMAGE'}

	# Show and then change pixel value in data

	>>> dm.data[0, 10, 10]
	115
	>>> dm.data[0, 10, 10] = 42
	>>> dm.data[0, 10, 10]
	42

	# Save to a new file

	>>> dm.to_asdf('test.asdf')
	>>> dm2 = rdm.open('test.asdf')
	>>> dm2[0, 10, 10]
	42
	>>> dm2.meta.exposure_start_time_mjd
	60000.0
