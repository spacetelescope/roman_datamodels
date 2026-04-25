Stnode Functionality
====================

As seen throughout :ref:`using-datamodels`, "node" objects are used to actually
handle and store the data for a data model. Indeed, if one opens an ASDF file
with a roman datamodel directly with `asdf.open` instead of
`roman_datamodels.datamodels.open`, the resulting object stored under the
``roman`` attribute will be a specialized `~roman_datamodels._stnode.DNode` object
rather than a `~roman_datamodels.datamodels.DataModel` object. Thus the stnode,
"node" objects form the data storage and manipulation backbone of the roman data
models.


Node Structure
**************

Stnode organizes the in the form of a tree structure. Where the
`roman_datamodels._stnode.DNode` "Node" objects act as keyword-value containers,
which branch to either other `~roman_datamodels._stnode.DNode` objects or to
the actual "leaf" data values (e.g. strings, numbers, arrays, etc.). These
`~roman_datamodels._stnode.DNode` objects are the core of stnode. Everything else
in stnode is built on top of these objects.

The `roman_datamodels._stnode.DNode` object itself is effectively a wrapper around
a python dictionary, which enriches the way one can interact with the data stored
within the node, and how RDM can handle the entire data-tree structure for things
like validation, serialization, etc. To end users, `~roman_datamodels._stnode.DNode`
implements the entire ``MutableMapping`` protocol interface, so users can interact
with it exactly as if they were interacting with any normal python dictionary.
So things like ``node["keyword"]``, ``node.keys()``, ``node.values()``, etc. all
work as one would expect with a normal python dictionary. For end users, the interface
has been enriched so that one can use the ``.`` operator to access the data attributes,
e.g. ``node.keyword`` works the same as ``node["keyword"]``. This is done to make
the stnode objects feel more "Pythonic" and act as though they were Python classes.


Dynamic Node Construction
*************************

A specialized "node" class, that is a node class with a specific name which maps
to a corresponding schema name, will be created and registered by
`~roman_datamodels._stnode` when the module is first imported. The schemas which
get this treatment are the "tagged" schemas defined within the ``datamodels-*``
manifest in the RAD package. Any "un-tagged" schemas in RAD will not have a
corresponding stnode object. Instead, the information they contain will be
stored in a `~roman_datamodels._stnode.DNode` object or standard python list.

These dynamically created "node" classes are subclasses of the
`~roman_datamodels._stnode.DNode` and contain additional functionally to handle
tagging information for ASDF functionally and referencing information stored within
the corresponding RAD schema. Most importantly, these "tagged-nodes" will keep
track of the ``tag`` information about the data.

These "tagged-nodes" are then turned into specific stnode objects via the
factories in `roman_datamodels._stnode._factories`. The way these factories work
is they process the ``tag`` value and strip out the unique name for the schema,
which gets turned into a name for the type that the factory will create.

.. note::

    If special methods are needed for a specific stnode object, then one needs
    to add class to `roman_datamodels._stnode._mixins` with the appropriate
    methods/properties under the name ``<expected-class-name>Mixin``. The
    factories will automatically pick up these mixins and mix them into the
    stnode object correctly when it is created.

These factories are looped over and invoked by the
`roman_datamodels._stnode._stnode` module which will be imported whenever
`roman_datamodels._stnode` is imported which will generate the stnode objects and
register them during that import. Note that this module is imported as part of
the `roman_datamodels.datamodels` module.


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
`roman_datamodels._stnode._converters` module. As part of this module, the
serialization and de-serialization logic is defined in the "converters" for each
of the "tagged" object base classes. The extension is then integrated into
ASDF by the `roman_datamodels._stnode._integration` module, as this module allows
the ASDF extension to be registered with ASDF without having to always import
``roman_datamodels`` whether or not it is used for a particular case. This is
a recommendation from ASDF so that the extension will have minimal impact on the
general ASDF performance for a given user.
