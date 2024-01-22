import importlib.resources

import rad.resources
import yaml
from asdf.versioning import AsdfVersion

from .versioning import USE_DEV

RAD_RESOURCES = importlib.resources.files(rad.resources)

# sort these so later we can use the order for registering asdf extensions in an order
# where newer manifests will be listed first (and used for writes)
MANIFEST_PATHS = sorted(
    [path for path in (RAD_RESOURCES / "manifests").iterdir() if path.suffix == ".yaml" and (USE_DEV or "dev" not in path.stem)],
    reverse=True,
)


def _load_manifest(path):
    with open(path) as f:
        return yaml.safe_load(f)


MANIFESTS = [_load_manifest(path) for path in MANIFEST_PATHS]
MANIFESTS_BY_VERSION = {AsdfVersion(manifest["id"].rsplit("/")[-1].split("-", maxsplit=1)[1]): manifest for manifest in MANIFESTS}

# unique
TAG_URIS = {tag_def["tag_uri"] for manifest in MANIFESTS for tag_def in manifest["tags"]}
