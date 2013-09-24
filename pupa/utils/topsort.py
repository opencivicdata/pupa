from collections import defaultdict


class CyclicGraphError(ValueError):
    pass


class Network(object):

    def __init__(self):
        self.nodes = []
        self.edges = defaultdict(list)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, fro, to):

        if fro not in self.nodes:
            self.add_node(fro)

        if to not in self.nodes:
            self.add_node(to)

        self.edges[fro].append(to)

    def leaf_nodes(self):
        deps = set([
            item for sublist in self.edges.values() for item in sublist
        ])
        return (x for x in self.nodes if x not in deps)

    def prune_node(self, node):
        self.nodes = [x for x in self.nodes if x != node]
        if node in self.edges:
            self.edges.pop(node)
        for fro, connections in self.edges.items():
            self.edges[fro] = [x for x in connections if x != node]

    def sort(self):
        while self.nodes != []:
            iterated = False
            for node in self.leaf_nodes():
                iterated = True
                self.prune_node(node)
                yield node
            if not iterated:
                raise CyclicGraphError("Cyclic graph")

