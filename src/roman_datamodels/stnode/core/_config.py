import copy
import threading
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import asdf
import yaml
from asdf import config as _asdf_config

from ._mixins import FlushOptions

__all__ = ["config_context", "get_config"]


class _StNodeConfig:
    """
    Class to handle external configuration of StNode objects.
    """

    def __init__(self) -> None:
        self._typeguard_enabled = False
        self._use_test_array_shape = False
        self._asdf_ctx: asdf.AsdfFile | None = None
        self._asdf_config: _asdf_config.AsdfConfig | None = None
        self._flush_option = FlushOptions.REQUIRED

    @property
    def typeguard_enabled(self) -> bool:
        """Access the typeguard enabled flag"""
        return self._typeguard_enabled

    @contextmanager
    def enable_typeguard(self) -> Generator[None, None, None]:
        """
        Context manager to temporarily enable typeguard for testing.
        """
        self._typeguard_enabled = True
        yield
        self._typeguard_enabled = False

    @property
    def use_test_array_shape(self) -> bool:
        """Access the use test array shape flag"""
        return self._use_test_array_shape

    @contextmanager
    def enable_test_array_shape(self) -> Generator[None, None, None]:
        """
        Context manager to temporarily enable the test array shape.
        """
        self._use_test_array_shape = True
        yield
        self._use_test_array_shape = False

    @property
    def flush_option(self) -> FlushOptions:
        """The default serialization flush option"""

        return self._flush_option

    @contextmanager
    def set_flush_option(self, flush_option: FlushOptions) -> Generator[None, None, None]:
        """
        Context manager to temporarily set the flush option.
        """
        self._flush_option = flush_option
        yield
        self._flush_option = FlushOptions.REQUIRED

    @property
    def asdf_ctx(self) -> asdf.AsdfFile:
        """Get the asdf context for the class."""

        if self._asdf_ctx is None:
            # ASDF has not implemented type hints so MyPy will complain about this
            # until they do.
            self._asdf_ctx = asdf.AsdfFile()  # type: ignore[no-untyped-call]

        return self._asdf_ctx

    @property
    def asdf_config(cls) -> _asdf_config.AsdfConfig:
        """Get the asdf config for the class."""
        if cls._asdf_config is None:
            cls._asdf_config = _asdf_config.get_config()  # type: ignore[no-untyped-call]

        return cls._asdf_config

    def get_schema(self, uri: str) -> dict[str, Any]:
        """
        Get the schema for the given URI

        Parameters
        ----------
        uri
            The URI of the schema to get

        Returns
        -------
        The raw schema dictionary for the given URI
        """
        # The yaml.safe_load is hinted as Any but really in our case we
        # expect a dict with string keys
        return yaml.safe_load(self.asdf_config.resource_manager[uri])  # type: ignore[no-any-return]


class _ConfigLocal(threading.local):
    """
    Local storage for configuration settings.
    """

    def __init__(self) -> None:
        super().__init__()
        self.config_stack: list[_StNodeConfig] = []


_global_config = _StNodeConfig()
_local = _ConfigLocal()


def get_config() -> _StNodeConfig:
    """
    Get the global configuration settings.
    """
    """
    Get the current config, which may have been altered by
    one or more surrounding calls to `core.config_context`.

    Returns
    -------
    asdf.config.AsdfConfig
    """
    if len(_local.config_stack) == 0:
        return _global_config

    return _local.config_stack[-1]


@contextmanager
def config_context() -> Generator[_StNodeConfig, None, None]:
    """
    Context manager to temporarily set configuration settings.
    """
    base_config = _global_config if len(_local.config_stack) == 0 else _local.config_stack[-1]

    config = copy.copy(base_config)
    _local.config_stack.append(config)

    try:
        yield config
    finally:
        _local.config_stack.pop()
