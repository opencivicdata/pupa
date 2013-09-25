from collections import defaultdict


class CyclicGraphError(ValueError):
    """
    This exception is raised if the graph is Cyclic (or rather, when the
    sorting algorithm *knows* that the graph is Cyclic by hitting a snag
    in the top-sort)
    """
    pass


class Network(object):
    """
    This object (the `Network` object) handles keeping track of all the
    graph's nodes, and links between the nodes.

    The `Network' object is mostly used to topologically sort the nodes,
    to handle dependency resolution.
    """

    def __init__(self):
        self.nodes = []
        self.edges = defaultdict(set)

    def add_node(self, node):
        """ Add a node to the graph (with no edges) """
        self.nodes.append(node)

    def add_edge(self, fro, to):
        """
        Add an edge from node `fro` to node `to`. For instance, to say that
        `foo` depends on `bar`, you'd say::

            `network.add_edge('foo', 'bar')`
        """

        if fro not in self.nodes:
            self.add_node(fro)

        if to not in self.nodes:
            self.add_node(to)

        self.edges[fro].add(to)

    def leaf_nodes(self):
        """
        Return an interable of nodes with no edges pointing at them. This is
        helpful to find all nodes without dependencies.
        """
        deps = set([
            item for sublist in self.edges.values() for item in sublist
        ])  # Now contains all nodes that contain dependencies.
        return (x for x in self.nodes if x not in deps)  # Generator that
        # contains all nodes *without* any dependencies (leaf nodes)

    def prune_node(self, node, remove_backrefs=False):
        """
        remove node `node` from the network (including any edges that may
        have been pointing at `node`).
        """
        self.nodes = [x for x in self.nodes if x != node]
        if node in self.edges:
            # Remove add edges from this node if we're pruning it.
            self.edges.pop(node)

        for fro, connections in self.edges.items():
            # Remove any links to this node (if they exist)
            if node in self.edges[fro]:
                if remove_backrefs:
                    # If we should remove backrefs:
                    self.edges[fro].remove(node)
                else:
                    # Let's raise an Exception
                    raise ValueError("""Attempting to remove a node with
                                     backrefs. You may consider setting
                                     `remove_backrefs` to true.""")

    def sort(self):
        """
        Return an iterable of nodes, toplogically sorted to correctly import
        dependencies before leaf nodes.
        """
        while self.nodes != []:
            iterated = False
            for node in self.leaf_nodes():
                iterated = True
                self.prune_node(node)
                yield node
            if not iterated:
                raise CyclicGraphError("Sorting has found a cyclic graph.")
