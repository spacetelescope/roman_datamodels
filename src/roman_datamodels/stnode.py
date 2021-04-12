"""
Proof of concept of using tags with the data model framework
"""

import jsonschema
from asdf.extension import Converter
from collections import UserList
from .stuserdict import STUserDict as UserDict
import asdf
import asdf.schema as asdfschema
import asdf.yamlutil as yamlutil
from asdf.util import HashableDict
#from .properties import _get_schema_for_property
from .validate import _check_type, _error_message

validate = True
strict_validation = True

def set_validate(value):
    global validate
    validate = bool(value)


validator_callbacks = HashableDict(asdfschema.YAML_VALIDATORS)
validator_callbacks.update({'type': _check_type})


def _value_change(path, value, schema, pass_invalid_values,
                 strict_validation, ctx):
    """
    Validate a change in value against a schema.
    Trap error and return a flag.
    """
    try:
        _check_value(value, schema, ctx)
        update = True

    except jsonschema.ValidationError as error:
        update = False
        errmsg = _error_message(path, error)
        if pass_invalid_values:
            update = True
        if strict_validation:
            raise jsonschema.ValidationError(errmsg)
        else:
            warnings.warn(errmsg, ValidationWarning)
    return update

def _check_value(value, schema, validator_context):
    """
    Perform the actual validation.
    """

    validator_resolver = validator_context.resolver

    temp_schema = {
        '$schema':
        'http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema'}
    temp_schema.update(schema)
    validator = asdfschema.get_validator(temp_schema,
                                          validator_context,
                                          validator_callbacks,
                                          validator_resolver)

    #value = yamlutil.custom_tree_to_tagged_tree(value, validator_context)
    validator.validate(value, _schema=temp_schema)
    validator_context.close()

def _validate(attr, instance, schema, ctx):
    tagged_tree = yamlutil.custom_tree_to_tagged_tree(instance, ctx)
    return _value_change(attr, tagged_tree, schema, False, strict_validation, ctx)

def _get_schema_for_property(schema, attr):
    subschema = schema.get('properties', {}).get(attr, None)
    if subschema is not None:
        return subschema
    for combiner in ['allOf', 'anyOf']:
        for subschema in schema.get(combiner, []):
            subsubschema = _get_schema_for_property(subschema, attr)
            if subsubschema != {}:
                return subsubschema
    return {}


class DNode(UserDict):

    _tag = None
    _ctx = None

    def __init__(self, node=None, parent=None, name=None):

        if node is None:
            self.__dict__['_data']= {}
        elif isinstance(node, dict):
            self.__dict__['_data'] = node
        else:
            raise ValueError("Initializer only accepts dicts")
        self._x_schema = None
        self._schema_uri = None
        self._parent = parent
        self._name = name
        # else:
        #     self.data = node.data

    # def __iter__(self):
    #     return NodeIterator(self)

    @property
    def ctx(self):
        if self._ctx is None:
            DNode._ctx = asdf.AsdfFile()
        return self._ctx
    
   
    def __getattr__(self, key):
        """
        Permit accessing dict keys as attributes, assuming they are legal Python
        variable names.
        """
        if key.startswith('_'):
            raise AttributeError('No attribute {0}'.format(key))
        if key in self._data:
            value = self._data[key]
            if isinstance(value, dict):
                return DNode(value, parent=self, name=key)
            elif isinstance(value, list):
                return LNode(value)
            else:
                return value
        else:
            raise AttributeError(f"No such attribute ({key}) found in node")

    def __setattr__(self, key, value):
        """
        Permit assigning dict keys as attributes.
        """
        if key[0] != '_':
            if key in self._data:
                if validate:
                    self._schema()
                    schema = self._x_schema.get('properties')
                    if schema is None:
                        # See if the key is in one of the combiners. 
                        # This implementation is not completely general
                        # A more robust one would potentially handle nested
                        # references, though that is probably unlikely
                        # in practical cases.
                        for combiner in ['allOf', 'anyOf']:
                            for subschema in self._x_schema.get(combiner, []):
                                ref_uri = subschema.get('$ref', None)
                                if ref_uri is not None:
                                    subschema = asdfschema._load_schema_cached(
                                                    ref_uri, self.ctx, False, False)
                                subsubschema = _get_schema_for_property(subschema, key)
                                if subsubschema != {}:
                                    schema = subsubschema
                                    break
                    else:
                        schema = schema.get(key, None)
                    if _validate(key, value, schema, self.ctx):
                        self._data[key] = value
                self.__dict__['_data'][key] = value
            else:
                raise AttributeError(f"No such attribute ({key}) found in node")
        else:
            self.__dict__[key] = value

    def to_flat_dict(self, include_arrays=True):
        """
        Returns a dictionary of all of the schema items as a flat dictionary.

        Each dictionary key is a dot-separated name.  For example, the
        schema element `meta.observation.date` will end up in the
        dictionary as::

            { "meta.observation.date": "2012-04-22T03:22:05.432" }

        """
        def convert_val(val):
            if isinstance(val, datetime.datetime):
                return val.isoformat()
            elif isinstance(val, Time):
                return str(val)
            return val

        if include_arrays:
            return dict((key, convert_val(val)) for (key, val) in self.items())
        else:
            return dict((key, convert_val(val)) for (key, val) in self.items()
                        if not isinstance(val, (np.ndarray, NDArrayType)))

    def _schema(self):
        """
        If not overridden by a subclass, it will search for a schema from 
        the parent class, recursing if necessary until one is found.
        """
        if self._x_schema is None:
            parent_schema = self._parent._schema()
            # Extract the subschema corresponding to this node.
            subschema = _get_schema_for_property(parent_schema, self._name)
            self._x_schema = subschema
    # def __getindex__(self, key):
    #     return self.data[key]

    # def __setindex__(self, key, value):
    #     self.data[key] = value

class LNode(UserList):

    _tag = None
    def __init__(self, node=None):
        if node is None:
            self.data = []
        elif isinstance(node, list):
            self.data = node
        else:
            raise ValueError("Initalizer only accepts lists")
        # else:
        #     self.data = node.data

    def __getitem__(self, index):
        value = self.data[index]
        if isinstance(value, dict):
            return DNode(value)
        elif isinstance(value, list):
            return LNode(value)
        else:
            return value

class TaggedObjectNode(DNode):
    """
    Expects subclass to define a class instance of _tag
    """

    @property
    def tag(self):
        return self._tag

    def _schema(self):
        if self._x_schema is None:
            self._x_schema = self.get_schema()
        return self._x_schema



    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        extension_manager = self.ctx.extension_manager
        tag_def = extension_manager.get_tag_definition(self.tag)
        schema_uri = tag_def.schema_uri
        schema = asdfschema._load_schema_cached(
            schema_uri, self.ctx, False, False)
        return schema

class TaggedListNode(LNode):

    @property
    def tag(self):
        return self._tag


class TaggedObjectNodeConverter(Converter):
    """
    This class is intended to be subclassed for specific tags
    """

    # tags = [
    #     "tag:stsci.edu:datamodels/program-*"
    # ]
    # types = ["stdatamodels.stnode.Program"]

    tags = []
    types = []

    def to_yaml_tree(self, obj, tags, ctx): 
        return obj

    def from_yaml_tree(self, node, tag, ctx):
        return (node)

