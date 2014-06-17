import pytest
from pupa.utils.topsort import Network, CyclicGraphError


def chash(cycles):
    """
    Hash a cycle, useful for comparing sets of cycles.

    This checks the sorted set of each of the nodes in the cycle. This
    is *not* a perfect check, but it's useful so that we can create a set
    of these hashes, and check that they all match.

    It's not perfect, since D -> A -> B will be the same as B -> A -> D,
    but since this is only used in the testing logic, we can ensure
    that we handle it correctly in the testcases.

    (Implicit warning: Don't use this anywhere important.)
    """
    return {"".join(sorted(set(x))) for x in cycles}


def test_sort_order_basic():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_node("C")

    network.add_edge("A", "B")
    network.add_edge("B", "C")

    assert (list(network.sort())) == ["A", "B", "C"]


def test_sort_order_double():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_node("C")

    network.add_edge("A", "B")
    network.add_edge("A", "C")
    network.add_edge("C", "B")

    # A  =>  B
    #       /
    # A => C

    assert (list(network.sort())) == ["A", "C", "B"]


def test_sort_order_staged():
    network = Network()

    network.add_node("A1")
    network.add_node("A2")
    network.add_node("A3")

    network.add_edge("A1", "A2")
    network.add_edge("A1", "A3")
    network.add_edge("A2", "A3")

    network.add_node("B1")
    network.add_node("B2")
    network.add_node("B3")

    network.add_edge("B1", "B2")
    network.add_edge("B1", "B3")
    network.add_edge("B2", "B3")

    network.add_edge("B1", "A1")

    network.add_node("C1")
    network.add_node("C2")
    network.add_node("C3")

    network.add_edge("C1", "C2")
    network.add_edge("C1", "C3")
    network.add_edge("C2", "C3")

    network.add_edge("C1", "A1")
    network.add_edge("C1", "B1")

    network.add_edge("C1", "B1")
    network.add_edge("B1", "A1")
    network.add_edge("A1", "C2")
    network.add_edge("A1", "C3")

    # with open("/home/tag/debug.dot", 'w') as fd:
    #     fd.write(network.dot())

    sorted_order = list(network.sort())

    assert sorted_order.pop(0) == "C1"
    assert sorted_order.pop(0) == "B1"
    assert sorted_order.pop(0) in ("A1", "B2")
    #                          ^^ This makes more sense after you dot debug it
    assert sorted_order.pop(0) in ("A1", "B2")


def test_cyclic_graph_error_simple():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_edge("A", "B")
    network.add_edge("B", "A")

    with pytest.raises(CyclicGraphError):
        list(network.sort())


def test_cyclic_graph_error_indirect():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_node("C")

    network.add_edge("A", "B")
    network.add_edge("B", "C")
    network.add_edge("C", "A")

    with pytest.raises(CyclicGraphError):
        list(network.sort())


def test_cyclic_graph_error_massive():
    network = Network()

    entries = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "A"]
    for i, e in enumerate(entries[:-1]):
        network.add_node(e)
        network.add_edge(e, entries[1 + i])

    with pytest.raises(CyclicGraphError):
        list(network.sort())


def test_link_before_nodes():
    network = Network()

    network.add_edge("A", "B")
    network.add_edge("B", "C")
    network.add_edge("C", "D")

    network.add_node("A")
    network.add_node("B")
    network.add_node("C")
    network.add_node("D")

    assert list(network.sort()) == ["A", "B", "C", "D"]


def test_internal_node_removal():
    network = Network()

    network.add_node("A")
    network.add_node("B")
    network.add_node("C")
    network.add_node("D")

    network.add_edge("A", "B")
    network.add_edge("B", "C")
    network.add_edge("C", "D")
    network.add_edge("A", "C")  # Useful for ensuring the ending list
    # is deterministic.

    # Ensure that we can't remove an internal node without a ValueError
    # by default.
    with pytest.raises(ValueError):
        network.prune_node("B")

    # OK. Now that we know that works, let's prune it harder.
    network.prune_node("B", remove_backrefs=True)

    # And make sure "B" is gone.
    assert list(network.sort()) == ["A", "C", "D"]


def test_dot_debug():
    network = Network()

    network.add_node("A")
    network.add_node("B")
    network.add_edge("A", "B")

    dot = network.dot()
    assert dot == "digraph graphname {A -> B;}"


def test_cycles_simple():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_edge("A", "B")
    network.add_edge("B", "A")
    assert chash(network.cycles()) == chash([("A", "B", "A")])


def test_cycles_complex():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_node("C")
    network.add_node("D")

    network.add_edge("A", "B")
    network.add_edge("B", "C")
    network.add_edge("C", "D")
    network.add_edge("D", "A")

    network.add_edge("D", "C")
    network.add_edge("C", "B")
    network.add_edge("B", "D")

    # with open("/home/tag/debug.dot", 'w') as fd:
    #     fd.write(network.dot())

    assert chash(network.cycles()) == chash([
        ('B', 'C', 'B'),
        ('C', 'D', 'C'),
        ('A', 'B', 'D', 'A')
    ])
