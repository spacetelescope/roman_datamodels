import asdf

NONUM = -999999
NOSTR = "dummy value"

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
        af = asdf.AsdfFile()
        af.tree = {"roman": node}
        af.write_to(filepath)

    return node
