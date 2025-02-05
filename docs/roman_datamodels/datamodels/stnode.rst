Stnode Functionality
====================

As seen throughout :ref:`using-datamodels`, "node" objects are used to actually
handle and store the data for a datamodel. Indeed, if one opens an ASDF file
with a roman datamodel directly with `asdf.open` instead of
`roman_datamodels.datamodels.open`, the resulting object stored under the
``roman`` attribute will be a `~roman_datamodels.stnode.DNode` object or sublclass
there of rather than a `~roman_datamodels.datamodels.DataModel` object. Thus the
stnode, "node" objects form the data storage and manipulation backbone of the
roman datamodels.

Data Nodes
----------

The stnode, "node" objects are all directly implemented in code as as part of the
``roman_datamodels.nodes`` module. This module contains nodes corresponding to all
the schemas and sub-structure objects defined within ``rad``.

.. note::

    Originally, the node objects were dynamically generated from the schema files
    as subclasses of `~roman_datamodels.stnode.DNode` or `~roman_datamodels.stnode.LNode`.
    However, due to the necessity of being able to create and work with the nodes
    bespoke utility functions were necessary to (partially or completely) fill out
    the data within the node so that the node was valid enough to be read or written
    by ASDF.

    Ultimately, this became equivalent to writing the node objects explicitly with
    python code, but without the advantages of having a static reference to develop
    against.

As part of the testing suite for ``roman_datamodels``, the schema files and the
Python code are closely compared against each other to ensure that the Python code
matches the state of the schema files. This does mean that the explicit Python objects
only really match the latest manifest version of ``rad`` that ``roman_datamodels``
was "built" against. This however does not mean that the node objects cannot handle
data older versions of ``rad`` schema files, instead it just means that the node's
explicitly defined attributes will not necessary match those in the older schema files.
The struncture of the `~roman_datamodels.stnode.DNode` and `~roman_datamodels.stnode.LNode`
objects is sufficient to easily handle this (link to DNode discussion here), but any
completion engines, IDEs, or direct examination of the node object code many not give
a clear or accurate picture of the data therein. Thus in these cases it is important
to refer to the older versions of ``rad``.


Core Node Types
***************

There are two core container node types `~roman_datamodels.stnode.DNode` and
`~roman_datamodels.stnode.LNode` which correspond to "dictionary" and
"list"-like data structures, respectively. As we will see, all the specific
stnode objects construct from a schema file will be built off these two classes.
Hence, general functionality of an stnode object should be implemented in these
two classes so that all stnode objects can inherit from them.

DNode
#####

The `~roman_datamodels.stnode.DNode` is the primary building block of the nodes
in ``roman_datamodels``. This is because most of the schemas in ``rad`` are based
around the ``type: object``, meaning they follow the form of a dictionary with
a specific set of keys. Note that in general for the ``rad`` schemas, the
``additionalProperties: true`` modifier for the object type is used, meaning that
in the corrispondinging node object, we must be able to support any sort of string
key in addition to the keys defined in the schema.

To support this "dictionary-like" behavior, the `~roman_datamodels.stnode.DNode`
object follows the `collections.abc.MutableMapping` protocol. This means that for
the most part `~roman_datamodels.stnode.DNode` based objects can interacted with
as if they were a dictionary. That is ``node["keyword"]`` can be used to access
the information stored under the keyword ``"keyword"`` in the node object.

While this is great as an initial interface and allows for easy interaction with
the `~roman_datamodels.stnode.DNode` based object's stored data. It is not very
Pythonic in the cases that one wants to access and work with a single data entry
in the node object. To address this, the `~roman_datamodels.stnode.DNode` object
implements a modification of the ``__getattr__`` method to allow for direct "dot"
(``.``) access to the data stored in the node object. For example the data stored
under the keyword ``"keyword"`` can be accessed via ``node.keyword``. Similarly,
there is a matching modification of the ``__setattr__`` method to allow for for
the setting of the data stored in the node object via the ``.`` operator; that is
``node.keyword = value``.

.. note::

    For data fields that are not defined in the ``rad`` schema corresponding to
    the node object, they cannot be initially set via the ``.`` operator. Meaning
    that if ``keyword`` is not a defined keyword under the ``properties:`` section
    of the ``rad`` schema, then ``node.keyword = value`` will raise an error. In
    this case the data can still be set via the ``[]`` operator using
    ``node["keyword"] = value``. Once this has occurred, then the data can be accessed
    and set via the ``.`` operator unless the data is removed using ``del node["keyword"]``.

Data Fields
^^^^^^^^^^^

In general, writing a node to an ASDF file requires that the data within that node
being able pass the matching ``rad`` schema for that node. Moreover, the ``rad``
schemas are developed for the end products, meaning that all the data that is expected
in the final products is detailed and required by the schema. This can pose awkward
issues, when running ``romancal`` as often not all data is flushed out in the node
by the end of the step, but will be filled in by subsequent steps. This is because
we need to be able to write a given datamodel to disk after any step in the pipeline.
To address this issue, some mechanism needs to be in place to fill in these missing
fields with dummy data so that the node can be written to disk.

This leads to the concept of "data fields" (or "fields" to be short). These are
the keyword entries under the ``properties:`` section of the ``rad`` schema, and
is these pieces of data which we are trying to fill in. The
`~roman_datamodels.stnode.field` `descriptor <https://docs.python.org/3/howto/descriptor.html>`_
forms the solution to this issue. Effectively, the ``~roman_datamodels.stnode.field``
is acting like the builtin `property` descriptor except that it modifies the behavior
of the ``getter`` function that is typically passed to `property`.

For `~roman_datamodels.stnode.field`, the ``getter`` function is used as the default
value generator function for the field. This means that when accessed, the `~roman_datamodels.stnode.field`
descriptor will first try to find the data in the node object itself; however, if the
data is not found, the ``getter`` function will then be called to generate and set the
default value for the field in the node before returning the value. This allows the
node object to be lazy about the data it contains, only filling in data when accessed
or set by the user, not when the node instance is created. For example

.. code:: python

    from roman_datamodels.stnode import core, rad

    class DummyNode(core.DNode):

        @rad.field
        def my_field(self) -> int:
            return 42

Represents a node object that has been created with a single field ``my_field``,
which is an integer with a default value of 42.

.. note::

    The `~roman_datamodels.stnode.field` descriptor is a specialized subclass of
    the builtin `property` descriptor, so aside from the modification of how the
    value get is handled, the `~roman_datamodels.stnode.field` descriptor behaves
    just like a normal `property`.

.. note::

    The introduction of the `~roman_datamodels.stnode.field` accomplishes another
    distinct goal aside from providing a mechanism to fill in missing data. It
    also statically (in Python code) defines the data fields that one normally
    can expect to find in a given node object. Indeed, it has been carefully
    annotated so that IDE completion engines will be able to provide useful completions.
    For example if a field's data is that of another field, the engine will be able
    to recognize this fact and provide completions for what data fields the user
    expects to find in the node object.

    Moreover, when cupled to the rest of `~roman_datamodels.stnode` objects, the
    `~roman_datamodels.stnode.field` also performs some lazy documentation generation
    wherein it will find the ``title`` and ``description`` keywords for that field
    in the corresponding ``rad`` schema and add those into an documentation included
    in the node object. This will only occur if the documentation ``__doc__`` string
    is accessed. This means things like ``help(node_type.field_name)`` and related
    will provide useful information about the field when the user is working interactively
    with a node.

.. warning::

    The fields for given node object will only match those defined in the version
    of ``rad`` which the node object was created against. This means that the
    nodes can only perform their automatic data filling for writing ASDF files
    for that particular version of ``rad``. Moreover, the fields and documentation
    can only match the version ``rad`` that was built against. This means that
    opening earlier or later versions of datamodels may result in situations where
    the fields and documentation are unreliable or incorrect. Indeed, the node
    will issue a warning that the there is a version difference in these cases.

    The nodes themselves are designed to be able to handle, modify, and write
    ASDF files in this case, but they will not be able to assist the user in a
    meaniful way (such as filling in values). In these cases, the node will not
    even try to flush out data fields.

LNode
#####

`~roman_datamodels.stnode.LNode` is the list-like node object. This object is used
to provide an interface for the ``type: array`` schemas in ``rad``. This "type" in
JSON schema is defines something akin to a Python list. In our case we are interpreting
it as a list of objects, so a base node class is needed to wrap these. Moreover,
these provide a convenience wrapper around the Python list object to provide a uniform
interface among the different node objects.

Similar to the `~roman_datamodels.stnode.DNode` object, the `~roman_datamodels.stnode.LNode`
object follows the `collections.abc.MutableSequence` protocol, indeed it is a subclass
of `collections.UserList`. This means that all the common methods for a Python `list`
object are available for the `~roman_datamodels.stnode.LNode` object. In particular,
accessing data stored in `~roman_datamodels.stnode.LNode` object is done via the ``[]``
operator, e.g. ``node[0]``.

RAD Node Types
**************

In order to tightly integrate with both ASDF and the ``rad`` schemas, `~roman_datamodels.stnode`
provides some higher level node objects which are subclasses of `~roman_datamodels.stnode.DNode`
or `~roman_datamodels.stnode.LNode`. The nodes that form the base classes for ``roman_datamodels.nodes``
objects all subclass specialized versions of these classes, namely:

    1. `~roman_datamodels.stnode.ObjectNode`, which extends `~roman_datamodels.stnode.DNode` with
       additional that assist in handling the data in the node object and linking it with the ``rad``
       schemas in-particular the ASDF handling for the data.
    2. `~roman_datamodels.stnode.ListNode`, which simply subclasses `~roman_datamodels.stnode.LNode`
       in order to provide a uniform descriptive interface like the `~roman_datamodels.stnode.ObjectNode`;
       note that this class does not add additional functionality to the `~roman_datamodels.stnode.LNode`,
       but could be used to add additional functionality if needed.
    3. `~roman_datamodels.stnode.ScalarNode`, which integrates in the ASDF handling features for the
       scalar data types.

These classes are then mixed with

    1. `~roman_datamodels.stnode.SchemaMixin`
    2. `~roman_datamodels.stnode.TagMixin`

To provide the necessary functionality to define all the core objects described by the ``rad`` schemas.
There are also some additional mixins that can be used to add additional functionality or descriptions
to the node objects, which will be discussed in more detail below.

.. note::

    These are all abstract classes meaning that the node implementation must define the necessary methods
    in order to be used.

Schema Nodes
############

All schemas in ``rad`` have a corresponding "schema" node present in ``roman_datamodels.nodes``, which
fall into the object, list, or scalar categories. These categories correspond to the following node types:

    1. `~roman_datamodels.stnode.SchemaObjectNode`,
    2. `~roman_datamodels.stnode.SchemaListNode`,
    3. `~roman_datamodels.stnode.SchemaScalarNode`.

All of which are simply mixes of the `~roman_datamodels.stnode.SchemaMixin` with the appropriate base
node.

.. note::

    Technically, tagged schemas do not fall into this category, instead they will be handled with
    the `~roman_datamodels.stnode.TagMixin`; however, that inherits from the `~roman_datamodels.stnode.SchemaMixin`.
    It however, implements some of the interface required by `~roman_datamodels.stnode.SchemaMixin` through
    the tag mechanisms. So broadly speaking, the tagged schemas and the schema nodes have the same general interface.

    All of this is to say that the direct schema node subclasses in ``roman_datamodels.nodes`` represent all the
    ``type: object`` schemas in the ``rad`` schemas which are not tagged.

To create a new schema node one simply needs to define the ``_asdf_schema_uris`` method in your class and then add your
fields using the ``~roman_datamodels.stnode.field`` descriptor as a decorator. For example:

.. code:: python

    class MySchemaNode(core.SchemaObjectNode):

        @classmethod
        def _asdf_schema_uris(cls) -> tuple[str, ...]:
            return ("asdf://stsci.edu/datamodels/roman/schemas/path_to_my_schema_uri",)

        @rad.field
        def my_field(self) -> int:
            return 42

For more examples see the source code for:

    1. `~roman_datamodels.stnode.SchemaObjectNode`:
        - `~roman_datamodels.nodes.Basic`: Follows directly from the example.
        - `~roman_datamodels.nodes.Common`: For inheriting directly from the above.

    2. `~roman_datamodels.stnode.SchemaListNode`:
        - There are no currently pure schema list nodes, only tagged ones.

    3. `~roman_datamodels.stnode.SchemaScalarNode`:
        - `~roman_datamodels.nodes.ExposureType`: Note this is an ``Enum`` node, which
          is described in better detail below.

.. note::

    The ``_asdf_schema_uris`` is used by the ``.asdf_schema_uris`` "class-property". For some reason,
    the `~abc.abstractmethod` decorator causes very strange behavior when combined with
    the `~roman_datamodels.stnode.classproperty` descriptor. Thus, the hidden method is used in the
    code base to define the value, but it should not be used outside of the defining class. Use the
    ``.asdf_schema_uris`` class-property instead.

.. note::

    Notice that ``_asdf_schema_uris`` is returning a tuple of strings. This is so that in the future
    multiple schema versions (and their URIs) can be represented by this single node object, rather
    than having to have multiple node objects for each schema version.

.. warning::

    The last URI in the ``_asdf_schema_uris`` tuple is considered to be the default/current schema
    for a node unless it is otherwise indicated when creating an instance. This means that new
    schema versions should be added to the end of the tuple.

    The ``-*`` version suffix for the schema URIs is not supported. This is so that the URIs are
    totally explicit and can be used to search for the schema files in the ``rad`` schemas directly.
    Moreover, this makes sure that specialized classes for a given URI can be supported as needed.

Tag Nodes
#########

In a similar vein to the schema nodes, all "tagged" (with respect to having a defined tag in the ``rad``
schemas manifest) schemas in ``rad`` have a corresponding "tagged node" object in ``roman_datamodels.nodes``.
Similarly to the schema nodes, these are

    1. `~roman_datamodels.stnode.TaggedObjectNode`,
    2. `~roman_datamodels.stnode.TaggedListNode`,
    3. `~roman_datamodels.stnode.TaggedScalarNode`.

All of which are simply mixes of the `~roman_datamodels.stnode.TagMixin` with the appropriate base.

To create a new sachema one simply needs to define the ``_asdf_tag_uris`` methnod on your class
followed by using the `~roman_datamodels.stnode.field` descriptor as a decorator to add your fields.
The ``_asdf_tag_uris`` must return a dictionary with full ``tag_uri`` as keys with entries being the
full ``schema_uri`` for the schema file. These should match up with a manifest entry in the ``rad``
schemas. For example:

.. code:: python

    class MyTaggedNode(core.TaggedObjectNode):

        @classmethod
        def _asdf_tag_uris(cls) -> dict[str, str]:
            return {
                "tag://stsci.edu/datamodels/roman/tags/my_tag": "asdf://stsci.edu/datamodels/roman/schemas/path_to_my_schema_uri"
            }

        @rad.field
        def my_field(self) -> int:
            return 42

For more examples see the source code for:

    1. `~roman_datamodels.stnode.TaggedObjectNode`:
        - `~roman_datamodels.nodes.Exposure`: Follows directly from the example.
        - `~roman_datamodels.nodes.Guidestar`.
        - `~roman_datamodels.nodes.IndividualImageMeta`.

    2. `~roman_datamodels.stnode.TaggedListNode`:
        - `~roman_datamodels.nodes.CalLogs`: Only difference is the inheritance from the example

    3. `~roman_datamodels.stnode.TaggedScalarNode`:
        - `~roman_datamodels.nodes.Filename`: Only difference is the inheritance from the example
        - `~roman_datamodels.nodes.FileDate`.
        - `~roman_datamodels.nodes.PrdVersion`.

.. warning::

    The dictionary should be ordered so that the latest tag will be the last entry in the dictionary.
    This works because Python 3+ does preserve the dictionary ordering. This ordering is important because
    it is what is used to determine the default tag that will be used when creating an instance. This
    tag is then used to fill in all the schema information.

Additional Node Types
#####################

In addition to the schema and tagged nodes, there are a few other node types that are used to introduce
further behavior to the nodes. These are:

    - `~roman_datamodels.stnode.ImpliedNodeMixin`: Signals the presence of a schema defined object
      which does not have its own dedicated scehma.
    - `~roman_datamodels.stnode.ExtraFieldsMixin`: Adds the ability to add extra fields to a node object
      that are not currently defined in the ``rad`` schemas.
    - `~roman_datamodels.stnode.EnumNodeMixin`: Forms the base class for scalar nodes which are defined
       in the ``rad`` schemas with an enumerated list of possible values, (e.g. has an ``enum:`` keyword).
    - `~roman_datamodels.stnode.ArrayFieldMixin`: Adds the ability to control the default size and shape
      for numpy array fields in a node object.
    - `~roman_datamodels.stnode.PatternDNode`: A specialized `~roman_datamodels.stnode.DNode` which
      is used to handle the ``patternProperties:`` keyword in the ``rad`` schemas.

Implied Nodes
^^^^^^^^^^^^^

The "implied nodes" are those nodes defined in the `~roman_datamodels.nodes` module which do not have
have a corresponding schema file in the ``rad`` schemas, but which are defined as an object by those
schemas. There are two circumstances in which this can occur:

    1. Under some property key, instead of a basic type or calling to another schema the ``rad`` schema
       instead defines a ``type: object`` that is nested under that key. In order to properly define
       defaults for these "sub" (implied) objects, a node object must be defined for them. In this case,
       one inherits first from `~roman_datamodels.stnode.ImpliedNodeMixin` followed by `~roman_datamodels.stnode.ObjectNode`.
    2. Under some property key, an ``allOf:`` combiner is used to define the data under that key.
       In this case, we are effectively defining a subclass inheriting from all the objects listed in
       that combiner. Again this requires an implied object to properly handlie the data. Note that
       this is an especially common case for the ``meta`` keyword in the ``rad`` schemas. In this case,
       one first inherits from `~roman_datamodels.stnode.ImpliedNodeMixin` followed by the appropriate
       nodes that are combined together by the ``allOf:`` combiner.

.. note::

    It is important to always have the `~roman_datamodels.stnode.ImpliedNodeMixin` as the first class
    in the inheritance list when defining an implied node object. This is so that `~roman_datamodels.stnode.ImpliedNodeMixin`
    can properly hook into the node object without its methods being overridden by the other classes.


When one creates an `~roman_datamodels.stnode.ImpliedNodeMixin` based object, one must define the ``_asdf_implied_by``
classmethod on the class. This method should return the ``type`` (not string name) for the object that implies the
object in question. Moreover, the name of the object should end with ``_<name of field>`` where the name of the field
is the keyword which is implying the object in question. For example:

.. code:: python

    class MyImpliedNode_Foo(core.ImpliedNodeMixin, core.ObjectNode):

        @classmethod
        def _asdf_implied_by(cls) -> type:
            return MyObjectNode

        @rad.field
        def my_field(self) -> int:
            return 42

    class MyObjectNode(core.ObjectNode):

        @rad.field
        def foo(self) -> MyImpliedNode_Foo:
            return MyImpliedNode_Foo()

Is how one would define an implied node object for the ``foo`` field in the ``MyObjectNode`` object.

For more examples see the source code for:
    - `~roman_datamodels.nodes.Guidewindow_Meta`: Follows directly from the example
    - `~roman_datamodels.nodes.WfiImage_Meta`.
    - `~roman_datamodels.nodes.WfiMosaic_Meta`.

.. note::

    This case represents the first case for an implied node object being used. If an all of combiner
    were used then ``core.Object`` node would be replaced by the appropriate node objects being combined.
    Observe that in that all of combiner we do not need an extra node class if a ``type: object`` definition
    is used to define one of the elements of the combiner. In this case, the fields listed under that
    will be added as fields to the implied node object.

.. note::

    If one needs to deviate from the naming scheme for the implied node object, then one can write their
    own ``asdf_implied_property_name`` classproperty on the implied node object which returns a string
    with the name of the property that implies the object. This will override the standard behavior of
    parsing the class name to determine the implied property name.


Extra Fields
^^^^^^^^^^^^

Historically, there have been cases where items acting like fields have been introduced into a node object
in `~roman_datamodels.nodes` which is not detailed in the ``rad`` schemas. This can be for a variety of
reasons, such as trying additional data functionality before making a formal schema change. To handle this

A node must be defined as a subclass of the `~roman_datamodels.stnode.ExtraFieldsMixin` and contain only
the fields that are not defined in the ``rad`` schemas. Then the main object needs to inherit from this object
in addition to its normal base class. For example:

.. code:: python

    class MyExtraFields(rad.ExtraFieldsMixin):

        @rad.field
        def my_extra_field(self) -> int:
            return 42

    class MyObjectNode(MyExtraFields, core.ObjectNode):

        @rad.field
        def my_field(self) -> int:
            return 42

Is how one can introduce the ``my_extra_field`` field into the ``MyObjectNode``
without it formally needing to be defined in the ``rad`` schema.

For more examples see the source code for:
    - `~roman_datamodels.nodes.FpsCommonMixin`: Follows directly from the example.`
    - `~roman_datamodels.nodes.TvacCommonMixin`.
    - `~roman_datamodels.nodes.RefCommonRef_InstrumentMixin`.

Enumerated Fields
^^^^^^^^^^^^^^^^^

In many cases, the ``rad`` schemas will enumerate the possible values for a given field
using the ``enum:`` keyword followed by a list. While not strictly necessary, it is very
nice to have a listing of the exact set of possible values which are statically defined
in an immutable way. To handle this, the `~roman_datamodels.stnode.EnumNodeMixin` is used.

Note that these enumerated fields have fallen into four catigories so far:

    1. A string value absent of any specifically defined tag or schema. In this
       case the `~roman_datamodels.stnode.StrNodeMixin` is used as part of the enum definition.
       In this case two classmethods need to be defined:

       - ``._asdf_container`` returning the type of node which contains the enum field.
       - ``._asdf_property_name`` returning the name of the field in the container node
         corresponding to the enumerated field.

    2. A string value defined within a standalone schema. In this case the
       `~roman_datamodels.stnode.SchemaStrNodeMixin` is used as part of the enum definition.
       This simply needs to define the required methods as if it was a `~roman_datamodels.stnode.SchemaScalarNode`.

    3. A string value defined within a standalone tagged schema. In this case the
       `~roman_datamodels.stnode.TaggedStrNodeMixin` is used as part of the enum definition.
       This simply needs to define the required methods as if it was a `~roman_datamodels.stnode.TaggedScalarNode`.

    4. An integer value absent of any specifically defined tag or schema. In this
       case the `~roman_datamodels.stnode.IntNodeMixin` is used as part of the enum definition.
       This needs to define the same methods as the `~roman_datamodels.stnode.StrNodeMixin`.

.. note::

    This list is subject to future expansion, but all the basic patterns are in place here.
    If one needs some other type like a tagged integer or something, then following one of
    the above is sufficient to define the new type in `~roman_datamodels.stnode`.

These are then combined with the `~roman_datamodels.stnode.RadEnum` class to create the
final enumerated node object. For example:

.. code:: python

    class MyEnumEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
        VALUE1 = "VALUE1"
        VALUE2 = "VALUE2"

        @classmethod
        def _asdf_container(cls) -> type:
            return MyObjectNode

        @classmethod
        def _asdf_property_name(cls) -> str:
            return "my_enum_field"

    class MyObjectNode(core.ObjectNode):

        @rad.field
        def my_enum_field(self) -> MyEnumEntry:
            return MyEnumEntry.VALUE1


Is how one defines an enumerated field in the ``MyObjectNode`` object. Similarly,
if we want to define an enumerated scalar which is defined in a schema file:

.. code:: python

    class MyEnumNode(rad.SchemaStrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
        VALUE1 = "VALUE1"
        VALUE2 = "VALUE2"

        @classmethod
        def _asdf_schema_uris(cls) -> tuple[str, ...]:
            return ("asdf://stsci.edu/datamodels/roman/schemas/path_to_my_schema_uri",)

is an example of how to do this. Note that if it were tagged a similar pattern would be followed.

For more examples see the source code for:

    1. `~roman_datamodels.stnode.StrNodeMixin`:
        - `~roman_datamodels.nodes.CoordinatesReferenceFrameEntry`: Follows directly from the example.
        - `~roman_datamodels.nodes.EphemerisTypeEntry`.
        - `~roman_datamodels.nodes.CalStepEntry`.

    2. `~roman_datamodels.stnode.SchemaStrNodeMixin`:
        - `~roman_datamodels.nodes.ExposureType`: Follows directly from the example.
        - `~roman_datamodels.nodes.WfiDetector`.
        - `~roman_datamodels.nodes.WfiOpticalElement`.

    3. `~roman_datamodels.stnode.TaggedStrNodeMixin`:
        - `~roman_datamodels.nodes.Origin`: Follows directly from the schema example with a different base class
        - `~roman_datamodels.nodes.Telescope`.

    4. `~roman_datamodels.stnode.IntNodeMixin`:
        - `~roman_datamodels.nodes.WcsinfoVparityEntry`: Follows directly from the `~roman_datamodels.stnode.StrNodeMixin`
          example with a different base class.

.. note::

    Notice that ``metaclass=rad.NodeEnumMeta`` is added to the class inheritance definition.
    This is to solve the issue with having multiple metaclasses, one from `abc.ABC` and the
    other from `enum.Enum`. This is a common issue when two a class inherits from classes with
    deferent metaclasses. The `~roman_datamodels.stnode.NodeEnumMeta` metaclass is a metaclass
    which mixes both the `abc.ABCMeta` and ``enum.EnumMeta`` metaclasses together and then is used
    to override the metaclass during the enum creation.

.. note::

    The `~roman_datamodels.stnode.RadEnum` class is a subclass of `enum.Enum` which modifies the
    ``str`` and ``repr`` behavior so that the value of the enum is returned rather than
    ``<enum name>.<enum value>`` in these cases. This is so that the enum truly plays like
    a `str` or `int` in the code base for things like table creation.

.. warning::

    Due to the automatic wrapping into the correct node object, passing a value that is not
    in the enum will raise an error from that enum. This is because the enum only allows
    for values it has defined. So in effect enum values will be validated during the
    setting process.

    This is a trade off against the removal of any "automatic validation" in ``roman_datamodels``
    so that the values for an enumerated field can be explicitly laid out in the code base.


Array Fields
^^^^^^^^^^^^

In many cases a node object will have a field which is a numpy array. In this case we often
want to be able to control the default shape of the array. This is because under "normal"
circumstances Roman has quite large array shapes, but these can be relatively resource intensive.
This is especially for testing and development where one might want to use smaller arrays so that
a large number of cases can be run faster with less memory. Moreover, for a given node object
the shapes of all the different array fields are generally linked to each other meaning a mechanism
so that these fields can understand this link is needed.

The `~roman_datamodels.stnode.ArrayFieldMixin` is used to handle this. Its usage simply requires it
to be mixed into the inheritance for a given node object. When introduced this class requires the user
to define two properties, each returning a tuple which both have the same number of elements.

    1. ``default_array_shape``: This is the shape of the array that we expect "normal" data to have.
    2. ``testing_array_shape``: This is a smaller shape that we can use for testing and development.

The ``.array_shape`` property can then be accessed inside a given field in order to get the shape
of the field given the circumstances of the object, i.e. if testing is going on. For example:

.. code:: python

    class MyArrayNode(core.ObjectNode, core.ArrayFieldMixin):
        @property
        def default_array_shape(self) -> tuple[int, ...]:
            return (2048, 2048)

        @property
        def testing_array_shape(self) -> tuple[int, ...]:
            return (512, 512)

        @rad.field
        def my_array_field(self) -> npt.NDArray[np.float64]:
            return np.zeros(self.array_shape, dtype=np.float64)


Is how one would define a node object with an array field that needs its shape controlled.

For more examples see the source code for:
    - `~roman_datamodels.nodes.WfiScienceRaw`: Follows directly from the example.`
    - `~roman_datamodels.nodes.WfiImage`: Includes an override noted below.
    - `~roman_datamodels.nodes.Ramp`.

.. note::

    The number of dimensions for the shape tuples should correspond to the largest number of dimensions
    among the fields in the node object. This way we only need a single tuple.

To signal that the testing shape should be used, the global datamodels configuration object provides
a context manager to return the testing shape. That is:

.. code:: python

    with core.get_config().enable_test_array_shape():
        # Code that needs the testing shape


.. warning::

    Once a field is initialize via the lazy fields under this context, its shape will be fixed
    and not return to the other shapes. Moreover, it may also cause other fields to conform with
    its shape even after the context manager exits. Thus it is best to perform all the testing
    operations for a given instance under this context manager before releasing the context manager

    In ``roman_datamodels`` the ``use_testing_shape`` fixture can be decorated onto a test function.
    It will automatically run the test function under this context manager.


If one wants to manually fix the default array shape to something other than the built in values
for a given node, then ``_array_shape=<shape>`` can be passed to the node object initializer. This
will set the default array shape to the given shape as a reference for all of the fields in that
instance. This cannot be overridden by the testing shape context manager, and in general is fixed
for that given instance.

.. note::

    The datamodels all have a required ``primary_array_name`` property which denotes the field
    that represents the primary array for the given node object. While not strictly required, it
    is normally used to "guess" the ``.array_shape`` value for an instance if that primary array
    has been set. This means that by default the `~roman_datamodels.stnode.ArrayFieldMixin` makes
    the assumption that the primary array has the largest number of dimensions among the fields.

    This is not always strictly true, but it holds for most node objects. If this is not the case,
    then one needs to override the ``_largest_array_shape_`` property with logic to generate the
    a shape for the array with the largest number of dimensions.

    Also observe that in most node objects with arrays involved, the "primary array" is the field
    with name "data". If this is not the case, then the user should override the ``primary_array_name``
    property with one which returns a string marking out the field that is the primary array.


Pattern Fields
^^^^^^^^^^^^^^

In a select set of cases, the ``rad`` schemas will define an object with a ``patternProperties:``
instead of ``properties:``. This is used to signal a dictionary like node whose keys
follow some regex pattern. In order to handle this, the `~roman_datamodels.stnode.PatternDNode`
is included. When defining this class one simply needs to define the ``_asd_implied_by`` classmethod
on the resulting type.

.. note::

    In all current cases in the ``rad`` schemas all of these patterned fields take place as
    implied objects. Thuse these will be inheriting from `~roman_datamodels.stnode.ImpliedNodeMixin`
    in addition to the `~roman_datamodels.stnode.PatternDNode`. These however, will need
    to define their own ``asdf_implied_property_name`` classproperty.

For example:

.. code:: python

    class MyObjectNode_Foo_PatternNode(core.ImpliedNodeMixin, core.ObjectNode):

        @classmethod
        def _asdf_implied_by(cls) -> type:
            return MyObjectNode

        @core.classproperty
        def asdf_implied_property_name(cls) -> str:
            return "foo"

        @classmethod
        def _asdf_key_pattern(cls) -> str:
            return r"^[a-z]+$"


    class MyObjectNode(core.ObjectNode):

        @rad.field
        def foo(self) -> MyImpliedNode_Foo_PatternNode[int]:
            return MyImpliedNode_Foo_PatternNode()

Defines the field ``foo`` in ``MyObjectNode`` as a "dictionary" (`~roman_datamodels.stnode.DNode`
object) with keys following the pattern ``r"^[a-z]+$"`` and values of type ``int``.

For more examples see the source code for:
    - `~roman_datamodels.nodes.AbvedgaoffsetRef_Data_PatternNode`: Follows directly from the example.`
    - `~roman_datamodels.nodes.ApcorrRef_Data_PatternNode`.
    - `~roman_datamodels.nodes.WfiImgPhotomRef_PhotTable_PatternNode`.

Data Models
-----------

The "data model" objects are all a mix between a given `~roman_datamodels.nodes`
and `~roman_datamodels.datamodels.DataModel`. This has not always been the case.

Historically, this was not the case. Instead the node objects were wrapped by the
`~roman_datamodels.datamodels.DataModel` object with pass-throughs including ``__getattr__``
and ``__getitem__`` directly into the node. This was done so that the node objects
would be the objects that would be directly interacting with ASDF serialization.
This was done in part because they used to be dynamically generated from the ``rad``
schemas.

However, now that the node objects are explicitly defined in the code base with
"field" system, it makes much more sense for the data models to inherit from the node
rather than wrapping it. This allows for the static analysis tools to make use of the
all the static information in the node objects when woring with data models instead
without the need of writing custom pass-throughs for each field in the data model object
corresponding with it.

.. note::

    Despite the inheritance, the strict ASDF handling is still done by the
    node objects only. This means that using a regular ``asdf.open`` call on a data model
    file will result in one getting a dictionary with key ``"roman"`` pointing at a
    node object NOT a data model object. The `~roman_datamodels.datamodels.open` function
    will directly return the correct datamodel object.

ASDF
----

The node objects are designed to be fully serializable to and from ASDF files. This
includes preserving any data which is added to the node instance that is not specifically
defined for it. Serialization however, is complicated by the fact that the node object's
defined data may not be filled in due to their lazy nature. This means that a given
node instance needs to "flush" itself out as part of ASDF serialization. By this we
mean generate the default values for fields that are not already filled in.

This is controlled via the `.flush` method on the node object. Which by default
will flush out only the "required" fields for the node object. By required, we mean
the fields indicated by the ``required:`` keyword in the ``rad`` schemas. This is
accomplished by the node looking up its own schema(s) and then combining all the ``required:``
field listings together. The node then loops over these fields, creating the default
value for every field that is not already filled in.

.. note::

    In the process of serializatiion, the node object will be storing default values
    for each of the fields it fills in. Meaning that those fields will now exist in
    the instance which was serialized.

    This is simply to limit the recreation of the same field on the same instance
    using the default value every time the instance is re-seralized. This recreation
    can be expensive for large arrays.

.. note::

    The serialization process by default does not include the "optional" fields in
    the schema if they have not been previously filled in on the instance, nor
    does it include an of the "extra" fields that maybe defined on the instance.

    By default serialization will only include what fields it minimally needs to
    in order to create a valid ASDF file.

.. warning::

    Passing a node to an ``asdf.AsdfFile`` object and then calling validate on that
    file will cause the node to flush out all its required fields. Indeed, calling
    the ``.validate`` method on a data model object will cause the same phenomenon.

Including More Fields
*********************

It is possible it influence the flushing process for ASDF. This however does require
using `~roman_datamodels.stnode.get_config` to get the global node configuration object.

This object has the context manager ``.set_flush_option`` which can be used to set the
flushing used. The options are listed in `~roman_datamodels.stnode.FlushOptions`:

    - ``FlushOptions.REQUIRED`` (or just ``"required"``): This is the default behavior
      which flushes only the required fields as stated in the ``rad`` schema(s).
    - ``FlushOptions.ALL`` (or just ``"all"``): This will flush all the fields
      in the schema meaning that all the required and optional fields defined in the
      ``rad`` schema(s) will be filled in.
    - ``FlushOptions.EXTRA`` (or just ``"extra"``): This will flush all the fields
      defined on the node object, including those that are not defined in the ``rad``
      schema(s).
    - ``FlushOptions.NONE`` (or just ``"none"``): This will not flush anything during
      serialization. This means that the node object will be serialized as is, so if
      the instance is not filled in with a required field, then the ASDF serialization
      will throw a validation error.

For example:

.. code:: python

    instance = MyObjectNode()
    with core.get_config().set_flush_option(core.FlushOptions.ALL):
        af = asdf.AsdfFile()
        af.tree["roman"] = instance
        af.write_to("test.asdf")

Will flush out all the fields including those that are not required.

.. note::

    The context manager is needed due to the fact that this sort of serialization
    option cannot be passed through to the ASDF converter during the serialization
    process. Thus the converter needs to be able to look up the value from somewhere
    during the serialization process, if we wish to have optional levels of serialization.
    behavior.

Extension
*********

``roman_datamodels`` provides a custom ASDF extension so that ASDF can handle
the stnode objects. This extension does not include the schemas used to build
the stnode objects, as the schemas are already included in extension provided by
the RAD package. The ASDF extension itself is defined in the `roman_datamodels.io`
module. This exitension is then registered with the ASDF library so that ASDF can
deserialize the stnode objects.
