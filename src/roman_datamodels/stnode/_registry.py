"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

OBJECT_NODE_CLASSES_BY_PATTERN = {}
LIST_NODE_CLASSES_BY_PATTERN = {}
SCALAR_NODE_CLASSES_BY_PATTERN = {}
SCALAR_NODE_CLASSES_BY_KEY = {}
NODE_CONVERTERS = {}
NODE_CLASSES_BY_TAG = {}
SCHEMA_URIS_BY_TAG = {}
