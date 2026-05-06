from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Self

from asdf.extension import ManifestExtension

from ._converters import ManifestNodeConverter, TaggedNodeConverter

if TYPE_CHECKING:
    from types import MappingProxyType

    from ._tagged import TaggedNode

__all__ = ("ManifestNode",)


class ManifestNode:
    """
    Intermediate "Node" class that is used to assist in ASDF serialization of TaggedNode(s)
        so that the extensions recorded in the ASDF file's history section are properly
        attributed to the correct manifest.
    """

    __slots__ = ("_data", "_tag")
    manifest_uri: ClassVar[str]
    tag_uris: ClassVar[MappingProxyType[str, type[TaggedNode]]]
    extension: ClassVar[ManifestExtension]

    # TODO: Fix the Any hint here
    def __init__(self, data: Any, tag: str):
        self._data = data
        self._tag = tag

    @property
    def data(self) -> Any:
        return self._data

    @property
    def tag(self) -> str:
        return self._tag

    @classmethod
    def _with_asdf_extension(cls) -> type[Self]:
        """
        Return ManifestNode with the appropriate ASDF extension added for the manifest
        """

        if not hasattr(cls, "extension"):
            cls.extension = ManifestExtension.from_uri(
                cls.manifest_uri,
                converters=(ManifestNodeConverter(cls), TaggedNodeConverter()),
            )

        return cls

    @staticmethod
    def factory(uri: str, tags: MappingProxyType[str, type[TaggedNode]]) -> type[ManifestNode]:
        """
        Factory method to create a ManifestNode subclass with the given manifest URI.
        """

        # We can just create a local subclass of ManifestNode instead of with
        #    type() since we don't actually care about the name of the class
        class _ManifestNode(ManifestNode):
            __slots__ = ()
            manifest_uri: ClassVar[str] = uri
            tag_uris: ClassVar[MappingProxyType[str, type[TaggedNode]]] = tags

        return _ManifestNode._with_asdf_extension()
