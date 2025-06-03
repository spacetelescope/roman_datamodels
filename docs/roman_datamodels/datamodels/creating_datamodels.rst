.. _creating-datamodels:

Creating Roman Datamodels
=========================

There are a few options to create a new datamodel. Each
has specific use cases and understanding what happens during
each option is vital to selecting which to use.

DataModel.create_minimal
........................

`roman_datamodels.datamodels.DataModel.create_minimal` inspects the datamodel schema
and creates a model that contains values that are unambiguously
defined in the schema. The resulting model will lack most
required attributes (since most attributes can be more than
one value) but will have the general structure expected by the
schema.

This method is most useful for pipeline code when a new
model is needed. For example, the source catalog step needs
to produce a new `roman_datamodels.datamodels.ImageSourceCatalogModel` model with contents
determined from the input `roman_datamodels.datamodels.ImageModel`. `roman_datamodels.datamodels.DataModel.create_minimal`
can be used to construct a model which is then filled out
with contents derived from the `roman_datamodels.datamodels.ImageModel` and then validated
to confirm that it contains all the required values.

DataModel.create_fake_data
..........................

`roman_datamodels.datamodels.DataModel.create_fake_data` inspects the datamodel schema
and creates a valid datamodel that contains "fake" data (for
example all required strings will be set to "?"). This is dangerous
to use within pipeline and user code as it greatly reduces
the utility of the schema validation.

The main use case for this method is unit tests where often
a small targeted operation is tested. In this case a valid
model is often needed but most of the model contents are not
of concern.

DataModel.__init__
..................

``DataModel.__init__`` constructs a new datamodel which optionally
contains the provided `roman_datamodels.stnode.TaggedObjectNode`. This is used when
`roman_datamodels.datamodels.open` constructs a new datamodel
from an ASDF file which contains the serialized contents of the
`roman_datamodels.stnode.TaggedObjectNode`. However this is less useful for pipeline
and/or test code where no node contents are available as the
produced datamodel will be invalid since it lacks all required
attributes.

Example
.......

To compare the above options let's consider a toy example ``WidgetModel``
with the following schema::

    %YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/reference_files/dark-1.0.0

    title: Widget model schema

    datamodel_name: WidgetModel

    type: object
    properties:
      meta:
        properties:
          telescope:
            description: "Name of the telescope"
            type: string
            enum: [ROMAN]
          target:
            description: "Target observed"
            type: string
        required: [telescope, target]
      data:
        tag: tag:stsci.edu:asdf/core/ndarray-1.*
        ndim: 3
        datatype: uint16
    required: [meta, data]

This schemas requires that the model have:

- ``meta.telescope`` which must be "ROMAN"
- ``meta.target`` which can be any string
- ``data`` which can be any 3 dimensional array containing 16 bit unsigned integers

`roman_datamodels.datamodels.DataModel.create_minimal` will construct a ``WidgetModel`` with only
``meta.telescope`` defined (since it must always be "ROMAN"). Both ``meta.target``
and ``data`` will not be defined and attempting to save this model will produce a
validation error (since both those attributes are required).

`roman_datamodels.datamodels.DataModel.create_fake_data` will produce a ``WidgetModel`` with all required
attributes containing "fake" values:

- ``meta.telescope`` will be "ROMAN" (the only allowed value)
- ``meta.target`` will be "?" (the default fake string value)
- ``data`` will contain all zeros

As all the required attributes are defined this model is valid and can be
saved.

``Datamodel.__init__`` will produce a ``WidgetModel`` with no attributes
defined. Attempting to save this model will result in a validation error
as it lacks all required attributes.
