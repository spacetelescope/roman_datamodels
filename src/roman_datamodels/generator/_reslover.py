"""
Define the custom model resolver so ASDF can resolve the schema references if needed.
"""
from typing import Sequence

from asdf.config import get_config
from datamodel_code_generator.reference import ModelResolver, get_relative_path

__all__ = ["RadModelResolver"]


class RadModelResolver(ModelResolver):
    """Modifications to the standard ModelResolver to support Rad $ref conventions"""

    def resolve_ref(self, path: Sequence[str] | str) -> str:
        manager = get_config().resource_manager

        if isinstance(path, str):
            joined_path = path
        else:
            joined_path = self.join_path(path)

        if joined_path in manager:
            # Note we need to be able to directly access the manager, issue opened on githug
            resolved_file_path = manager._mappings_by_uri[joined_path].delegate.get_file_path(joined_path)

            return get_relative_path(self._base_path, resolved_file_path).as_posix() + "#"

        return super().resolve_ref(path)
