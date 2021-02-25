import _collections_abc
# import sys as _sys

# from itertools import chain as _chain
# from itertools import repeat as _repeat
# from itertools import starmap as _starmap
# from keyword import iskeyword as _iskeyword
# from operator import eq as _eq
# from operator import itemgetter as _itemgetter
# from reprlib import recursive_repr as _recursive_repr
# from _weakref import proxy as _proxy

# try:
#     from _collections import deque
# except ImportError:
#     pass
# else:
#     _collections_abc.MutableSequence.register(deque)

# try:
#     from _collections import defaultdict
# except ImportError:
#     pass

class STUserDict(_collections_abc.MutableMapping):

    # Start by filling-out the abstract methods
    def __init__(*args, **kwargs):
        if not args:
            raise TypeError("descriptor '__init__' of 'STUserDict' object "
                            "needs an argument")
        self, *args = args
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if args:
            dict = args[0]
        elif 'dict' in kwargs:
            dict = kwargs.pop('dict')
            import warnings
            warnings.warn("Passing 'dict' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        else:
            dict = None
        self._data = {}
        if dict is not None:
            self.update(dict)
        if kwargs:
            self.update(kwargs)
    __init__.__text_signature__ = '($self, dict=None, /, **kwargs)'

    def __len__(self): return len(self._data)
    def __getitem__(self, key):
        if key in self._data:
            return self._data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)
    def __setitem__(self, key, item): self._data[key] = item
    def __delitem__(self, key): del self._data[key]
    def __iter__(self):
        return iter(self._data)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key):
        return key in self._data

    # Now, add the methods in dicts but not in MutableMapping
    def __repr__(self): return repr(self._data)
    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["_data"] = self.__dict__["_data"].copy()
        return inst

    def copy(self):
        if self.__class__ is STUserDict:
            return STUserDict(self._data.copy())
        import copy
        data = self._data
        try:
            self._data = {}
            c = copy.copy(self)
        finally:
            self._data = data
        c.update(self)
        return c

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
