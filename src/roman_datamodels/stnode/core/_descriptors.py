from __future__ import annotations

import sys
from collections.abc import Callable
from functools import wraps
from threading import RLock
from typing import Any, Generic, TypeVar, cast

__all__ = ["classproperty", "lazyproperty"]

_NotFound = object()

_T = TypeVar("_T")


class classproperty(property, Generic[_T]):
    """
    This has been adapted from the `astropy.utils.decorators.classproperty` class

        Effectively, this should be identical except for the addition of some type
        hints and making this perminantly lazy.
    """

    def __new__(cls, fget: Callable[[Any], _T] | None = None, doc: str | None = None) -> classproperty[_T]:
        if fget is None:
            # Being used as a decorator--return a wrapper that implements
            # decorator syntax
            def wrapper(func: Callable[[Any], _T]) -> classproperty[_T]:
                return cls(func)

            return wrapper  # type: ignore[return-value]

        return super().__new__(cls)

    def __init__(self, fget: Callable[[Any], _T], doc: str | None = None) -> None:
        self._lock = RLock()  # Protects _cache
        self._cache: dict[type | None, _T] = {}

        fget = self._wrap_fget(fget)

        super().__init__(fget=fget, doc=doc)

        # There is a buglet in Python where self.__doc__ doesn't
        # get set properly on instances of property subclasses if
        # the doc argument was used rather than taking the docstring
        # from fget
        # Related Python issue: https://bugs.python.org/issue24766
        if doc is not None and sys.flags.optimize < 2:
            self.__doc__ = doc

    def __get__(self, obj: Any | None = None, objtype: type | None = None) -> _T:
        val = self._cache.get(objtype, _NotFound)
        if val is _NotFound:
            with self._lock:
                # Check if another thread initialised before we locked.
                val = self._cache.get(objtype, _NotFound)
                if val is _NotFound:
                    val = self.fget.__wrapped__(objtype)  # type: ignore[union-attr]
                    self._cache[objtype] = val  # type: ignore[assignment]

        return cast(_T, val)

    def getter(self, fget: Callable[[Any], _T]) -> property:
        return super().getter(self._wrap_fget(fget))

    def setter(self, fset: Callable[[Any, _T], None]) -> property:
        raise NotImplementedError(
            "classproperty can only be read-only; use a metaclass to implement modifiable class-level properties"
        )

    def deleter(self, fdel: Callable[[Any], None]) -> property:
        raise NotImplementedError(
            "classproperty can only be read-only; use a metaclass to implement modifiable class-level properties"
        )

    @staticmethod
    def _wrap_fget(orig_fget: Callable[[Any], _T] | classmethod[Any, Any, _T]) -> Callable[[Any], _T]:
        if isinstance(orig_fget, classmethod):
            orig_fget = orig_fget.__func__

        @wraps(orig_fget)
        def fget(obj: type) -> _T:
            return orig_fget(obj.__class__)

        return fget


class lazyproperty(property, Generic[_T]):
    """
    This has been adapted from the `astropy.utils.decorators.classproperty` class

        Effectively, this should be identical except for some type hints and the
        removal of everything except the fget and doc
    """

    def __init__(self, fget: Callable[[Any], _T], doc: str | None = None) -> None:
        super().__init__(fget, None, None, doc)
        # We only accept an actual function passed in not creation conventionally
        # regular property does not distinguish between the two
        self._key = self.fget.__name__  # type: ignore[union-attr]
        self._lock = RLock()

    def __get__(self, obj: Any | None, owner: type | None = None) -> _T:
        try:
            obj_dict = obj.__dict__
            val = obj_dict.get(self._key, _NotFound)
            if val is _NotFound:
                with self._lock:
                    # Check if another thread beat us to it.
                    val = obj_dict.get(self._key, _NotFound)
                    if val is _NotFound:
                        # In the condition where fget is always not None, unlike
                        # general property
                        val = self.fget(obj)  # type: ignore[misc]
                        obj_dict[self._key] = val
            return cast(_T, val)
        except AttributeError:
            if obj is None:
                # Ignoring this case because I don't want to overload things
                return self  # type: ignore[return-value]
            raise
