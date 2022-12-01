.. _datamodels:

About datamodels
================

The purpose of the data model is to abstract away the peculiarities of
the underlying file format.  The same data model may be used for data
created from scratch in memory, or loaded from ASDF files or some future file
format.

Each model instance is created to contain a variety of attributes and data that
are needed for analysis or to propagate information about the file and the
contents of the file. For example, the `roman_datamodels.datamodels.ImageModel` class
has the following arrays associated with it:

    - ``data``: The science data
    - ``dq``: The data quality array
    - ``err``: The error array

Along with data arrays the datamodel also contains information about the
observation that can include the observation program, exposure information,
pointing information and processing steps.
