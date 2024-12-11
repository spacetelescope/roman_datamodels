from pathlib import Path

import asdf

NONUM = -999999
NOSTR = "?"
NOFN = "none"

MESSAGE = "This function assumes shape is 2D, but it was given at least 3 dimensions"


def save_node(node, filepath=None):
    """
    Save the node to a file if there is a file path given, and return the node.

    Parameters
    ----------
    node: DNode
        The node to save.
    filepath: str
        (optional) File name and path to write model to.
    """

    if filepath:
        # Force sync filename with file path if we are saving to a file
        if "meta" in node and "filename" in node["meta"]:
            # Need the __class__ to avoid issues for tvac and fps
            node["meta"]["filename"] = node["meta"]["filename"].__class__(Path(filepath).name)

        af = asdf.AsdfFile()
        af.tree = {"roman": node}
        af.write_to(filepath, all_array_compression="lz4")

    return node
