"""Association Generator

The Association Generator takes a list of items, an Association Pool, and
creates sub-lists of those items depending on each item's attributes. How the
sub-lists are created is defined by Association Rules.

For more, see the :ref:`documentation overview <asn-overview>`.

"""

# Take version from the upstream package


# Utility
def libpath(filepath):
    """Return the full path to the module library."""
    from os.path import abspath, dirname, join

    return join(dirname(abspath(__file__)), "lib", filepath)


from .association import *  # noqa: F403, E402
from .association_io import *  # noqa: F403, E402
from .exceptions import *  # noqa: F403, E402
from .generate import *  # noqa: F403, E402
from .lib.process_list import *  # noqa: F403, E402
from .main import *  # noqa: F403, E402
from .pool import *  # noqa: F403, E402
from .registry import *  # noqa: F403, E402
