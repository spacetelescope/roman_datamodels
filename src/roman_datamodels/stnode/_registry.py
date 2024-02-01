"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

OBJECT_NODE_CLASSES_BY_TAG = {}
LIST_NODE_CLASSES_BY_TAG = {}
SCALAR_NODE_CLASSES_BY_TAG = {}
SCALAR_NODE_CLASSES_BY_KEY = {}
NODE_CONVERTERS = {}
