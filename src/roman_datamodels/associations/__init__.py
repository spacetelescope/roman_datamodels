"""Association Generator

The Association Generator takes a list of items, an Association Pool, and
creates sub-lists of those items depending on each item's attributes. How the
sub-lists are created is defined by Association Rules.

For more, see the :ref:`documentation overview <asn-overview>`.

"""
from .association import *  # noqa: F403
from .association_io import *  # noqa: F403
from .exceptions import *  # noqa: F403
from .generate import *  # noqa: F403
from .lib.process_list import *  # noqa: F403
from .main import *  # noqa: F403
from .pool import *  # noqa: F403
from .registry import *  # noqa: F403

# Take version from the upstream package


# Utility
def libpath(filepath):
    """Return the full path to the module library."""
    from os.path import abspath, dirname, join

    return join(dirname(abspath(__file__)), "lib", filepath)
