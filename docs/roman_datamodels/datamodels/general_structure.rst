General Structure of a Roman datamodel
======================================

Overview
........

When opening a Roman ASDF data file as such::

  import roman_datamodels as rdm
  dm = rdm.open('some_roman_data.asdf')

What is returned is a Python object that on the surface is very similar to its
JWST equivalent, and provides all the relevant methods that make sense for Roman
(for example, those that relate to FITS issues in JWST are not needed for Roman).

It should be mentioned that all Reference files are also in ASDF format; each
reference file type has its own datamodel, whose structure has a standard set
of attributes between all reference files (fairly small), and quite a bit of
variation in the rest of the attributes.

Some of the most relevant methods are:

- **clone:** an in-memory copy
- **save:** save in a new file
- **close:** close the file
- **get_primary_array_name:** the attribute name of the primary array
- **shape**: shape of primary array
- **to_flat_dict:** return all items as a flat dictionary with keys as dotted
  attribute paths such as ``meta.exposure.start_time``
- **items:** return all items as a list of key, value pairs, with keys expressed as
  dotted attribute paths
- **get_crds_parameters:** obtain all parameters used to select reference files
  in CRDS
- **validate:** check datamodel against schemas
- **info:** display information about the contents
- **search:** search for attributes or values

While ASDF permits a wide variety of legal attribute names, the convention is that Roman
only uses attribute name that are legal Python variable names. This is so they can be
used as Python object attributes. Using the above example for the keys that ``to_flat_dict``
returns, that permits using ``dm.meta.exposure.start_time`` to obtain the value of that attribute
instead of ``dm.tree['roman']['meta']['exposure']['start_time']``. The latter can still be used
if you enjoy typing lots of brackets and quotes instead of periods.

Generally, the large data related items, such as the image array and associated data quality,
error, and other arrays are at the top of the contents of the roman attribute. The related
metadata is to be found under the meta attribute.
