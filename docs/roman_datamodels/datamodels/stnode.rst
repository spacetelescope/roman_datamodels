Stnode Functionality
====================

As seen throughout :ref:`using-datamodels`, "node" objects are used to actually
handle and store the data for a datamodel. Indeed, if one opens an ASDF file
with a roman datamodel directly with `asdf.open` instead of
`roman_datamodels.datamodels.open`, the resulting object stored under the
``roman`` attribute will be a `~roman_datamodels.stnode.DNode` object rather
than a `~roman_datamodels.datamodels.DataModel` object. Thus the stnode, "node"
objects form the data storage and manipulation backbone of the roman datamodels.

Dynamic Generation
------------------

Unfortunately, the stnode objects are not directly written in the roman
datamodels codebase. Instead, they are dynamically generated from the schema
files defined in the RAD schema package. The reason for this is that the schema
files are treated as the "truth" for how the data should be stored rather than
any Python code. The dynamically generated object types are a way to facilitate
this without massive code duplication. This of course means that issues
concerning the stnode objects such as schema violations can be difficult to
debug, without an understanding of the schema files and their connection with
the stnode objects.


Node Types
**********

There are two main container node types `~roman_datamodels.stnode.DNode` and
`~roman_datamodels.stnode.LNode` which correspond to "dictionary" and
"list"-like data structures, respectively. As we will see, all the specific
stnode objects construct from a schema file will be built off these two classes.
Hence, general functionality of an stnode object should be implemented in these
two classes so that all stnode objects can inherit from them.

Currently, these two objects are implemented so that they follow the
dictionary or list interface; meaning that, they can be accessed via the ``[]``
operator (``node["keyword"]`` or ``node[0]``). However, for the case of the
`~roman_datamodels.stnode.DNode` objects, keys can also be used to directly
access the data attributes of the object via the Python ``.`` operator
(``node.keyword``). This is so that the `~roman_datamodels.stnode.DNode`
objects "look" like they are nice Python derived types.

.. warning::

    Because the `~roman_datamodels.stnode.DNode` "attributes" are actually like
    they are Python dictionary key, using the ``__getattr__`` to enable ``.``
    access, things like ``dir(node)``, IDE autocompletion, and some other Python
    introspection tools will not work as expected. In some cases this may result
    in spurious warnings about accessing undefined attributes. It also means
    that one should be referencing the schema files to understand what
    attributes are available for a given stnode object.

    This information can be found using the ``.info()`` method. This method will
    be a pass through to the `asdf.AsdfFile.info` method.


Dynamic Node Construction
*************************

A specialized "node" class, that is a node class with a specific name which maps
to a corresponding schema name, will be created and registered by
`~roman_datamodels.stnode` when the module is first imported. The schemas which
get this treatment are the "tagged" schemas defined within the ``datamodels-*``
manifest in the RAD package. Any "un-tagged" schemas in RAD will not have a
corresponding stnode object. Instead, the information they contain will be
stored in a `~roman_datamodels.stnode.DNode` or `~roman_datamodels.stnode.LNode`
object, depending on the schema in question.

.. note::

    The creation of stnode "node" types might occur when a user opens an ASDF
    file containing Roman data, as ASDF will load stnode as part of its
    de-serialization process. However, due to how Python imports work this
    should only happen once.

The specific stnode objects will be subclasses of the
`~roman_datamodels.stnode.TaggedObjectNode` or
`~roman_datamodels.stnode.TaggedListNode` classes. These classes are extensions
of the `~roman_datamodels.stnode.DNode` and `~roman_datamodels.stnode.LNode`
classes which have extensions to handle looking up the schema information for on
the fly data validation. In particular, they will track the ``tag`` information
contained within the manifest from RAD.

These "tagged-nodes" are then turned into specific stnode objects via the
factories in `roman_datamodels.stnode._factories`. The way these factories work
is they process the ``tag`` value and strip out the unique name for the schema,
which gets turned into a name for the type that the factory will create.

.. note::

    If special methods are needed for a specific stnode object, then one needs
    to add class to `roman_datamodels.stnode._mixins` with the appropriate
    methods/properties under the name ``<expected-class-name>Mixin``. The
    factories will automatically pick up these mixins and mix them into the
    stnode object correctly when it is created.

These factories are looped over and invoked by the
`roman_datamodels.stnode._stnode` module which will be imported whenever
`roman_datamodels.stnode` is imported which will generate the stnode objects and
register them during that import. Note that this module is imported as part of
the `roman_datamodels.datamodels` module.


Scalar Nodes
************

In addition to the objects described above, there are the "scalar node"
objects, which are created from multiple inheritance of
`~roman_datamodels.stnode.TaggedScalarNode` and a scalar type. These objects are
used to represent the schemas under the ``tagged_scalars`` directory in RAD.
Those schemas are used to decorate a few common scalar ``meta`` fields with
additional information for the archive and sdp. Due to how the ``meta`` keyword
is assembled (via multiple combiners), ASDF has a hard time traversing the
schemas to look for this information. Thus, these scalar nodes are tagged so that
ASDF has a hook to find them without trying a recursive search of the schema
files. If this issue is resolved in the future, or the metadata under ``meta``
is reorganized, then scalar node concept can be removed from the codebase.

.. note::
    The scalar nodes determine the type they mix together with
    `~roman_datamodels.stnode.TaggedScalarNode` via, the ``SCALAR_TYPE``
    constant dictionary defined in `roman_datamodels.stnode._factories`. This
    dictionary keys off the ``type`` keyword that all schemas have to define. If
    a new type needs to be added, then one needs to add a new entry to this
    dictionary.


Validation
----------

The stnode objects are designed to attempt to validate the data they contain or
have set in them against the schema information in RAD. This is typically done
on the fly when the data is set via the ``.`` interface; however, ASDF by
default will validate the data stored in the node against its schema during both
serialization and de-serialization.

In order to avoid the overhead of re-validating all of the data in a node when
one thing is updated (this can induce a lot of overhead), the stnode objects
will attempt to parse a given "tagged-node's" schema down so that it is only
validating the field being updated. It performs the validation by attempting to
construct in-memory an ASDF-schema representing just the portion of the schema
it needs to validate just that single field against.  It then passes that schema
into the ASDF validation routines to check the data. Unfortunately, this is not
a perfect process nor is it particularly robust. It is possible for a schema to
have fields that the parse down process cannot handle, or use JSON-schema
constructs which the parser is unaware of. In these cases, validation might
raise an error or pass invalid data.

.. warning::

    The only validation process that is guaranteed to validate the data
    correctly is the full ASDF validation process. This is because ASDF will be
    using the full schema and be checking everything against it. The on-the-fly
    validation's parsing may create unreliable validation scenarios.

.. note::

    In order to avoid the "on-the-fly" validation process, one can set values in
    a node/datamodel via the dictionary, ``[]``, interface instead of the ``.``
    interface. This is because the ``[]`` purposely bypasses the on-the-fly
    validation process. Thus in general it is recommend that one uses the ``.``
    interface for setting values in a node/datamodel, and only using the ``[]``
    when one needs to store temporary invalid data in a node/datamodel. The use
    ``[]`` runs the risk of placing the node/datamodel in a state where it
    cannot be serialized to ASDF.


ASDF
----

The stnode objects are designed to be serializable to and from ASDF files. As
noted above, the stnode objects wrapped by the
`~roman_datamodels.datamodels.DataModel` are the actual objects which are
serialized to ASDF not the `~roman_datamodels.datamodels.DataModel` object
itself.

``roman_datamodels`` provides a custom ASDF extension so that ASDF can handle
the stnode objects. This extension does not include the schemas used to build
the stnode objects, as the schemas are already included in extension provided by
the RAD package. The ASDF extension itself is defined in the
`roman_datamodels.stnode._converters` module. As part of this module, the
serialization and de-serialization logic is defined in the "converters" for each
of the three "tagged" object base classes. The extension is then integrated into
ASDF by the `roman_datamodels.stnode._integration` module, as this module allows
the ASDF extension to be registered with ASDF without having to always import
``roman_datamodels`` whether or not it is used for a particular case. This is
a recommendation from ASDF so that the extension will have minimal impact on the
general ASDF performance for a given user.
