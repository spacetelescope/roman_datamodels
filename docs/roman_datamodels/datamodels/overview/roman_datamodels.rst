.. _rdm_overview:

===========================
Overview of the RDM Package
===========================

The ``roman_datamodels`` (RDM) package is intended to provide the Python implementation
to support working with data for the Nancy Grace Roman Space Telescope as described by
the schemas in the ``rad`` package. The ``rad`` package is primarily a collection of
ASDF-flavored JSON schemas which describe ultimately describe the data products and
reference files used by the Roman Calibration Pipeline ``romancal`` (RCAL).

Originally, functioned by creating so called ``node`` objects at runtime to represent
each of the schemas contained in ``rad``. Effectively, these ``node`` objects were a
fancy Python dictionary wrapper that attempted to link into ASDF's validation system
and provided a convenience interface that made Python code employing it look like
standard object-oriented Python code. This approach is not ideal for several reasons:

#. When errors occur, it one ends up with trace-backs referencing Python objects which
   are not statically viewable. That is one cannot directly view code that is representative
   of the object in question. Effectively, this means that to debug a particular data model,
   issue one had to examine the schema in ``rad`` itself and then try and figure out how
   that mapped to the ``node`` object.
#. The ``node`` system was not statically analyzable meaning that basic tools like ``pylint``
   and IDEs could not provide any useful information or checks on code involving the ``node``
   objects. This made working with RDM even more error prone.
#. The ``node`` object validation system was effectively a partial implementation of
   a JSON schema validation library. This is not ideal as it was not a complete implementation,
   nor was it particularly well-tested. This has led to a number of bugs concerning the
   setting of invalid values in the ``node`` objects and then being unable to realize them
   until the model is written to disk. Moreover, there were other bugs concerning parts of
   JSON schema, which were totally valid JSON-schema, but which were not supported by the
   ``node`` object validation system.
#. The ``node`` objects had to be "wrapped" in the actual ``DataModel`` objects with call
   downs into the ``node`` objects. This created a conceptual disconnect between the data
   and the code that RCAL was working with. This has caused problems with developers trying
   to work with partially instantiated data models and other related problems.
#. While the ``node`` objects were intended to limit the amount of repentance in developing
   RDM, in some ways they were actually not saving any work. This is because testing and
   creation of data models still required one to add constructors for each data model. Doing
   this was effectively the same as implementing something like a ``dataclass`` in Python.

The new approach that has been taken by RDM is to use an automatic code generator to create
Python code that is representative of the structures imposed by the ``rad`` schemas. The primary
benefit of this approach is that it creates static Python code that directly leverages Python's
object model and type system. This means that there is no longer a need for a distinction between
``node`` and ``DataModel`` objects. Instead, the code generator creates subclasses of some root
``DataModel`` class which simply fill in the fields needed to represent the data as described by
the schemas in ``rad``.

RDM Package Structure
=====================

The use of the automatic code generator has allowed RDM to be restructured into 3 main sub-packages:

#. ``core``: which defines the root ``DataModel`` classes which define the Python API for working
   with the data models.
#. ``datamodels``: which contains the generated code for the data models and the supporting code to provide
   ASDF support for RDM.
#. ``generator``: which defines the automatic code generator to turn ``rad`` schemas into Python code.

This organization delineates a clear separation of code responsibilities. In particular, it separates
the ``generator`` code from everything else, which is important as the ``generator`` code is not intended
or needed for use at runtime. Instead, the ``generator`` code is only needed when RDM is being installed
from source.

RDM Core
--------

RDM core defines the primary Python API and overall structure of the RDM data models. Instead of using
a bespoke "data model" implementation, RDM core instead uses the ``pydantic`` package to define its
data models. This is for three reasons:

#. There is a ready-made implementation of a JSON-schema to Python code generation package, ``datamodel-code-generator``.
#. ``pydantic`` is a well-tested and well-supported package, which is specifically designed to be used
   for data validation. This means that once the code is generated, pydantic can handle all of the
   data validation for RDM.
#. ``pydantic`` has many useful built in features, which can be leveraged by RDM. For example, it has
   several introspection features which can be used by RDM to assist with things such as ASDF serialization
   and retrieval of metadata from the ``rad`` schemas. Moreover, ``pydantic`` is extremely well optimized
   and efficient which should help with the performance of RDM.

RDM core defines two main pydantic models:

#. `roman_datamodels.core.BaseDataModel`, which forms the foundation for all data models in RDM. In particular it defines
   all of the recursive functionality needed to support the RDM Python API, even for data models which are not direct
   data products.
#. `roman_datamodels.core.DataModel`, which is the root data model for all data products and reference files in RDM. It is
   a subclass of `roman_datamodels.core.BaseDataModel` and adds the functionality needed to support the direct interface
   employed by RCAL and other code that uses RDM. In particular, it is used to define any data model which can be directly
   written to an ASDF file.

The majority of the API responsibilities for RDM are split between these two classes, where `roman_datamodels.core.BaseDataModel`
contains the functionality that is common to all data models regardless of whether or not they can be serialized to ASDF or used
by RCAL, while `roman_datamodels.core.DataModel` contains the functionality necessary for the data model to be serialized directly
to ASDF and used by RCAL. Note that in general, end users of RDM will be mainly working with `roman_datamodels.core.DataModel`
subclasses which include all of the functionality of `roman_datamodels.core.BaseDataModel`.

Extending RDM Core
******************

In addition to `roman_datamodels.core.BaseDataModel` and `roman_datamodels.core.DataModel`, RDM core provides a mechanism,
`roman_datamodels.core.ExtendedDataModel`, to extend the Python functionality of and data model derived from a tagged
``rad`` schema. This is useful when one needs specific functionality for a particular data model, but that functionality
is not applicable to all data models. To create an extended data model, one simply creates a subclass of
`roman_datamodels.core.ExtendedDataModel` in ``roman_datamodels.core.extended``, which specifically defines the
``schema_uri`` class attribute to match the ``id`` (schema uri) for the schema describing the data in RAD omitting the version
number encoded in the ``id``. That is if the ``id`` is ``asdf://something/my_schema-1.0.0```, then the ``schema_uri`` will
be ``asdf://something/my_schema``. This is to enable support for multiple versions of the same schema. Note that RDM enforces
via unit tests the convention that the extended data model class name is the same name as the expected name for the generated
model prefixed with a ``_``. For example, if the expected name for the generated model is ``MyModel`` then the extended data
model class name should be ``_MyModel``. This is to prevent name collisions with the generated model.

Once an `roman_datamodels.core.ExtendedDataModel` is defined for a given schema, then the code generator will automatically
select it as a base class for the data model(s) matching the provided ``schema_uri``. Any additional functionality that needs
to be added or "mixed-in" to the data model can then be directly added to the new class.

RDM Core API
************

Users should in general be directly working with subclasses of `roman_datamodels.core.DataModel` and not directly with
`roman_datamodels.core.BaseDataModel`, so the discussion here will be for the API of `roman_datamodels.core.DataModel`.

In addition to the ASDF serialization and deserialization support `roman_datamodels.core.DataModel` provides the following
methods for working with data models:

- `roman_datamodels.core.DataModel.copy`: which enables shallow and deep copying of data models. Note that this should be
  used instead of the standard Python ``copy/deepcopy`` functions or the Pydantic ``.model_copy`` method. This is because
  if the `roman_datamodels.core.DataModel` is built directly from an ASDF file it will contain a reference to the ASDF file
  object. Copying this reference will interfere with the ``.model_copy`` method employed by Pydantic and setting a ``__copy__``
  or ``__deepcopy__`` method on the data model creates issues with ``.model_copy``, which is employed by the
  `roman_datamodels.core.BaseDataModel` in several places.

- `roman_datamodels.core.BaseDataModel.get_archive_metadata`" this can be used directly on the model types them selves to
  retrieve the archive related metadata for the data model which has been encoded into the ``rad`` schema.

- `roman_datamodels.core.DataModel.make_default`: this can be used to create a fully "valid" data model filled with "dummy"
  values. Note that the values filled in are simply ones permitted by the schema and are not necessarily "sensible" values,
  and any values added by this method should be properly checked by the end user before use. This method has two important
  functions in RDM:

  #. To provide a way to create a data model before all the information intended for that data model is available. This
     occurs often in RCAL as each step needs to a place to put the values it computes before all the values are ready.
     The convention there is to simply "fill-in" the data model as the step(s) progress. However, both Pydantic and ASDF
     validation methods will take issue with any required fields that have not been "filled-in" yet.
  #. To provide an easy way to create "dummy" models for the purposes of testing RDM, RCAL, or other code that uses RDM.
     This allows one to realize a model that one is only interacting with via the Python API without having to create a
     "true" data set for that model.

.. note::

   In order to support the creation of "default" array data for array fields, the ``rad`` schemas need to add the
   additional metadata keyword ``default_shape`` to the metadata describing the array. This shape is assumed to be
   a reasonable shape for the array, and should not be considered to be the "true" shape of the data. Instead it is
   intended to be an example of a "reasonable-shape" for the data.

   This is a departure from the convention that ``rad`` does not include anything that is not strictly needed for the
   the general metadata. However, it is a reasonable departure as it is not otherwise possible to infer a reasonable
   shape for an array for a given data model field. This is because there is a fair amount of variation in the specific
   shapes expected.

- `roman_datamodels.core.BaseDataModel.pause_validation`: This is a context manager that can be used to temporarily disable
  validation of all models in RDM. Note that it needs to be called once on the outer-most data model in order to disable
  validation on all models while the context manager is active. This is useful for three cases:

  #. Working with intermediate values during RCAL processing, which may not be valid data as defined by the ``rad`` schemas,
     but which will be valid once the processing is complete.
  #. Improving performance of code that is iteratively updating a data model many times. Even though the data models all
     employ Pydantic's extremely fast and efficient validation system, it still introduces a non-trivial amount of overhead
     which can cause significant slow downs if the data model is being updated many times, where one only really cares about
     the final state of the model being valid.
  #. Working with RDM data models during active development when the ``rad`` schema data specifics are in flux. This is
     mostly to ease Pipeline developers' lives when working with RDM data models during active development of the ``rad``
     schemas themselves, and should not be employed in once the schemas are finalized.

  Note that this context has two argument options ``revalidate_on_exit=True`` and ``revalidate_on_exit=False``. When
  ``revalidate_on_exit=True`` (the default), when the context manager exits the model used to create the context will
  revalidate itself and all its sub-models, while when ``revalidate_on_exit=False`` the model will not revalidate itself
  (and a warning will be issued). Turning off revalidation should only really be employed during development of code but
  not in finalized code.

- `roman_datamodels.core.DataModel.asdf_validate`: Call ASDF's validation system on the data model. There are currently
  a few edge cases where the code generator does not full encode the schema's restrictions into the resulting Pydantic
  model, but which ASDF will still catch. See discussion below.

- `roman_datamodels.core.DataModel.create_model`: The general constructor/initializer for RDM data models. This method
  will attempt to construct a data model given any of the normal ways one may try to construct the data model. In particular,
  it accepts other data models, paths to ASDF files, ASDF file objects, and nested dictionaries. It will then attempt to
  construct a fully validated model from the provided input.

- `roman_datamodels.core.DataModel.from_asdf`: This is a class method that can be used to construct a data model from an
  ASDF file object or path to an ASDF file object. Indeed, it is what is employed by `roman_datamodels.core.DataModel.create_model`
  when it is passed an ASDF file object or path to an ASDF file object. Note that when called it may force the resulting
  data model to either "manage" (close the file when done) the ASDF file object or not. This is controlled by whether or
  not an already opened ASDF file is passed or not.

- `roman_datamodels.core.DataModel.to_asdf`: This will write a data model instance to the file name provided to the method.
  This serves as the primary method to write the data model to an ASDF file.

- `roman_datamodels.core.DataModel.info`, `roman_datamodels.core.DataModel.search`, and `roman_datamodels.core.DataModel.schema_info`:
  These are pass through methods to ASDF's `asdf.AsdfFile.info`, `asdf.AsdfFile.search`, and `asdf.AsdfFile.schema_info` methods
  respectively. They have the same interface as those methods, they simply make sure to call the method on the correct ASDF file
  object.

In addition to these methods `roman_datamodels.core.DataModel` also provides a Python-dictionary like interface to the data
model. Namely, one can use the ``[]`` operator to get and set values in the data model using the string names of the data fields
as if the data model were a dictionary.

.. note::

   By default validation of fields set by ``[]`` is turned on. However, it can be turned off for an instance indefinitely
   by calling `roman_datamodels.core.BaseDataModel.set_validate_setitem` with the argument ``False`` on the instance. This
   will cause validation to be paused while the item is being set, where the model is not re-validated once the item is set.
   However, in this case a warning will be issued to indicate that it is possible the model maybe in an invalid state.

Furthermore, one can set any non-schema defined field on the model using either the Python "dot" interface. e.g. ``model.my_extra_field =...``
or the ``[]`` operator. e.g. ``model['my_extra_field'] = ...``. Note that these fields will not be validated by Pydantic or
ASDF but they will be serialized to and from ASDF files (if the field's type is supported by ASDF). Moreover, in addition
to allowing extra fields, the existence of a field under a given string name can be checked using the usual Python ``in``
operator. e.g. ``'my_field' in model``.

Finally, since all RDM data models are based on Pydantic models, the entire Pydantic model API is available to RDM data, see
the Pydantic API documentation for details.

RDM Core Pydantic Adaptors
**************************

In addition to the ``roman_datamodels.core.DataModel`` and ``roman_datamodels.core.BaseDataModel`` classes, RDM core also
defines a number of Pydantic type adaptors in ``roman_datamodels.core.adaptors``. These adaptors are used to enable Pydantic
to handle and validate types outside its normally supported types (see, here for native types). Currently, RDM needs adaptors
for:

- `astropy.time.Time`
- `astropy.units.Unit`
- `astropy.units.Quantity`
- `numpy.ndarray`

However, if types which are not defined using Pydantic or one of its supported types are needed in addition to the above
types one can create a type adaptor in the similar fashion to the existing adaptors. Effectively this is creating a
class with a ``__get_pydantic_core_schema__`` and ``__get_pydantic_json_schema__`` method which can be annotated using
the `typing.Annotated` type annotation onto the type that needs to be adapted. The Pydantic documentation has more details.

.. note::

   Pydantic does support having arbitrary types directly annotated in fields of a model if the ``arbitrary_types_allowed``
   (see here) configuration option is set to ``True``. However, this will significantly limit RDM's ability to perform
   validation of the data models, so it is currently avoided.

RDM Data Models
---------------

This sub-package simply contains all the models actually generated by the code generator. It also contains the code necessary
to create the ASDF extension which enables ASDF to seamlessly handle the RDM data models. In theory, the ASDF extension
does not need to be altered to support any new schemas added to ``rad``. However, not all corner cases have been explored
or tested. So it is possible alterations to the ASDF extension may be needed in the future to support future ``rad`` schemas.
Note that the unit tests do their best to ensure that every data model is properly supported by the ASDF extension, so
if there is some issue the unit tests should detect it.

.. note::

   Due to some of the changes being made to ``rad`` in order to make it both simpler and support the automatic code generator,
   some of the ASDF tags have been altered. In order to support the older tags, the ASDF converter for RDM will automatically
   translate the old tags to their new equivalents while reading an existing ASDF file. However, it will raise a `DeprecationWarning`
   and cannot write files using those tags.

RDM Generator
-------------

The code generator for RDM is a sub-package of RDM, which is not needed at runtime. It is only needed when RDM is being installed
or when models need to be regenerated during development (it is also needed during testing). Its purpose is to take the schemas
in ``rad`` and generate Python code based of `roman_datamodels.core` which represent the data formatting encoded in the schemas.

The code generator itself is not a bespoke code generator, instead is an extension of the ``datamodel-code-generator`` package.
It was chosen as the basis for the code generator because:

#. It supports generating Python code from JSON schemas.
#. It is the package recommended by Pydantic for generating Pydantic models from JSON schemas.
#. It is well supported and widely used package for generating Python code from JSON schemas.

Overview of ``datamodel-code-generator``
****************************************

The main downside to ``datamodel-code-generator`` is that its extension interface is not well documented, as it was
originally imagined as a self-contained CLI tool. However, extensions are needed to support extensions of JSON-schema
like what ASDF employs with its tag system.

Effectively, the ``datamodel-code-generator`` is divided into two main parts:

#. A JSON-schema parser which parses the JSON-schema into a usable Python object.
#. A code generator which takes the parsed JSON-schema and writes Python code.

RDM's code generator's extensions are mainly focused on the JSON-schema parser rather than the code generator itself.
This is because most of the specifics requiring extensions to ``datamodel-code-generator`` are due to the ASDF
JSON-schema extension. In particular, "teaching" the JSON-schema parser how to handle ASDF tags.

The extensions to the ``datamodel-code-generator``'s JSON-schema parser are:

#. Extensions to the the ``datamodel_code_generator.parser.json_schema.JsonSchemaObject``, which is what the parser uses
   to make the initial read of a JSON-schema. RDM extends this object to ``roman_datamodels.generator._schema.RadSchemaObject``
   to add the following functionality:

   - ``id``: is needed because the JSON-schema draft specification that ``datamodel-code-generator`` is based on is a
     newer version that the one used by ASDF. In particular, in later JSON-schema drafts, the ``id`` key word was changed
     to ``$id`` to signify that it is used for references between schemas. Currently, ADSF does not support this newer
     ``id`` keyword. So the code generator needs to know to look for the ``id`` keyword and interpret it as the ``$id``.
   - ``tag``: is needed to support ASDF tag references in schemas. Normally, JSON-schema only references other schemas
     via its ``$ref`` system, where-in the ``$ref`` keyword is used as a reference to some ``id/$id`` for some other schema.
     JSON-schema interpret's this as "including" the referenced schema within the schema making the reference at the point
     the reference is made. ASDF uses "tag" references in a similar fashion; however, the ``tag`` confers extra information
     about the reference. In particular, it indicates that the "tagged-field" will have a YAML-tag matching the ``tag`` value
     in the YAML representation of the data (where this YAML-tag confers "type" information about the data). For the RDM
     generator's purposes, if a ``tag`` is one defined by ``rad`` then the generator can simply treat that tag as if it was
     a ``$ref`` because that ``$ref`` will be a different data model class written by the generator anyways, so the type
     information is implicitly encoded by how the generator writes Python code. If a ``tag`` is not defined by ``rad`` then
     the generator extension assumes that there is a Pydantic type adaptor for that tag and will attempt to find one to use.
   - ``tag_uri``: while not directly encoded in the ``rad`` schemas themselves, is encoded in the ``rad`` schema manifest,
     and is directly related to the schema in question and its ultimate function in RDM. Thus, the schema parser is extended
     so that it can go ahead and "look-up" the ``tag_uri`` for a given schema and pass it along to the code generator.

#. Extensions to the ``datamodel_code_generator.reference.ModelResolver``, which is what the parser uses to resolve references
   between different schemas and models. That is determine things like what ``$ref`` refers to in the Python code and any
   inheritance relationships in the Python code. Unfortunately, both ASDF and ``rad`` make different assumptions on how to
   turn ``$ref`` into file locations for schemas than the ``datamodel-code-generator`` does, in particular it uses the
   `Swagger $ref <https://swagger.io/docs/specification/using-ref/>`_ convention. So an the extension
   ``roman_datamodels.generator._reference.RadModelResolver`` to the ``ModelResolver`` is needed in order to "plug-in"
   ASDF's schema-reference system into the ``datamodel-code-generator``'s schema-reference system.

#. Extensions to the actual parser itself ``data_model_code_generator.parser.json_schema.JsonSchemaParser``, which is
   what actually parses the JSON-schema into a usable Python object for the code generator are needed to incorporate the
   above extensions into the parser. In addition to this, the parser also handles:

   - Detection of when to use and selection of Pydantic type adaptors.
   - Injection of extra information for the code generator itself to write into the Python code.
   - Setting all the inputs to the parser object to those needed to support the optional features employed by RDM.

All of the modifications to the code generator itself are less intrusive. In particular, those modifications only involve
adding additional extra information to the ``jinja2`` templates used by the code generator to ultimately format the final
python code.

.. note::
   The ``BaseModel.jinja2``, ``ConfigDict.jinja2``, and ``RootModel.jinja2`` templates (found in
   ``src/roman_datamodels/generator/custom_templates``) are direct copies of the templates employed by the ``datamodel-code-generator``
   with changes to ``BaseModel.jinja2`` and ``RootModel.jinja2`` to inject the ``schema_uri`` and ``tag_uri`` information
   (``ConfigDict.jinja2`` is a direct copy needed because of how the templates reference each other).


Known Issues with RDM
=====================

There are a few known issues with RDM, at this time:

#. The use of ``patternProperties`` to enforce regex restrictions on dictionary keys
   is currently not encoded by the code generator into the Pydantic model. This currently
   only effects the ``phot_table`` field of `roman_datamodels.datamodels._generated.WfiImgPhotomRefModel`.
   Meaning that the keys of the ``phot_table`` dictionary are not validated by Pydantic at this
   time.

   Further investigation is needed to determine if this is a limitation of or bug in Pydantic or
   ``datamodel-code-generator``. If a work around is found, it will be implemented or contributed upstream.

#. One cannot use a blank (no ``properties`` keywords) ``type: object`` in a ``rad`` schema to represent an
   expected arbitrary object, if that object is not going to be a Python dictionary. This is because
   the ``data-model-code`` generator has made the decision that this JSON-schema construct should represent
   a pure Python dictionary, which is a reasonable assumption as this is the only practical way to encode
   what one would expect to be a Python dictionary in a JSON-schema. This is slightly different than how
   ASDF treats this, which is that the data will be anything that is represented as an object in the YAML,
   which includes both Python dictionaries and Python objects. This can be side-stepped by simply not decorating
   schema keys with ``type: object`` unless they are expected to be Python dictionaries. Currently, this only
   effects the ``coordinate_distortion_transform`` field of `roman_datamodels.datamodels._generated.DistortionRefModel`, which
   was decorated in ``rad`` with ``type: object`` but with the expectation that it would be an `astropy.modeling.Model`
   of undetermined type at this time. Unfortunately, there is not a good way to indicate an arbitrary `astropy.modeling.Model`
   in ASDF schemas, so instead the solution is to not decorate this field with any restriction meaning that Pydantic
   will validate any Python object that is passed to this field.

#. The `roman_datamodels.core.DataModel.make_default` method is intended to be a replacement for the
   ``maker_utils`` in previous versions of RDM. However, ``make_default`` is much more limited than the ``maker_utils``
   were. This is because ``make_default`` systematically generates each default value rather than using the
   hand-coded values that the ``maker_utils`` employed. To the greatest extent possible, ``make_default`` will
   should generate the values that the ``maker_utils`` did, but there are some special cases were that was not practical.
   This is a reasonable compromise as it is much easier to maintain ``make_default`` than the ``maker_utils`` due to the
   fact no (or minor) changes are needed to support ``make_default`` rather than extensive changes to the ``maker_utils``
   every time a schema is added or updated in a non-trivial way.

#. The data models ``__init__`` method is not as flexible with inputs as it was previously. This is because the
   ``__init__`` method provided by Pydantic had many benefits over the ``__init__`` method that was previously being
   used. While Pydantic does allow one to alter the ``__init__`` for a data model, it was not practical to do so
   in a way that enabled both the functionality of the old ``__init__`` method and the benefits of the default
   ``__init__`` provided by Pydantic. Thus the `roman_datamodels.core.DataModel.create_model` method was created
   in order to have the same basic interface as the old ``__init__`` method, while preserving the default
   Pydantic ``__init__`` method.

#. The ``tagged_scalar`` schemas needed to be folded back into the ``basic`` schema in ``rad``. This is because
   they created large amounts of complexity (lots of tiny work arounds) in the code generator and the resulting
   code for only the benefit of enabling ASDF's `asdf.AsdfFile.schema_info` the limited utility of finding archive
   information related to an existing ASDF file. Essentially, the ``tagged_scalar`` schemas were a "hack" to get
   around limitations with the use of nested ``allOf`` combiners in the ``rad`` schemas and how they interacted
   with ``schema_info``'s search system. This still had the limitation that one needed a realized ASDF file or
   data model in order to initiate the search.

   Instead, RDM now provides the `roman_datamodels.core.BaseDataModel.get_archive_metadata` method which can be
   run on the model types themselves rather than on a realized model or ASDF file. This method ultimately returns
   exactly the same meta data as what ``schema_info`` was being used for, but with the additional benefit of not
   requiring a model instance itself.

#. The "requirement" that "Pydantic adaptors" need to be constructed for third-party ASDF serializable types.
   As already noted, this is not a true requirement because we can allow arbitrary types directly in the Pydantic
   model. However, this creates severe limitations on the validation that Pydantic can perform on the data model.
   Currently, the four third-party types that have been needed by RDM have been quite stable with no additions to
   them in a long time. So the "requirement" is not a major issue at this time. However, if it becomes an issue to
   write Pydantic adaptors, allowing arbitrary types directly in the Pydantic model can be revisited.

#. The current version of the ``datamodel_code_generator.parser.json_schema.JsonSchemaParser`` requires fairly
   extensive modifications in order to properly function. This however has been fixed upstream in this
   `PR <https://github.com/koxudaxi/datamodel-code-generator/pull/1783>`_ which has not appeared in a release yet.
   Once it appears, this issue will be resolved.
