import random
from pupa.utils.topsort import Network, CyclicGraphError


def test_sort_order_basic():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_node("C")

    network.add_edge("A", "B")
    network.add_edge("B", "C")

    # A => B => C
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
    assert sorted_order.pop(0) == "A1"


def test_cyclic_graph_error_simple():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_edge("A", "B")
    network.add_edge("B", "A")
    try:
        assert list(network.sort()) is None, "Sort returned - expected CyclicGraphError"
    except CyclicGraphError:
        pass


def test_cyclic_graph_error_indirect():
    network = Network()
    network.add_node("A")
    network.add_node("B")
    network.add_node("C")

    network.add_edge("A", "B")
    network.add_edge("B", "C")
    network.add_edge("C", "A")
    try:
        assert list(network.sort()) is None, "Sort returned - expected CyclicGraphError"
    except CyclicGraphError:
        pass


def test_cyclic_graph_error_massive():
    network = Network()

    entries = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "A"]
    for i, e in enumerate(entries[:-1]):
        network.add_node(e)
        network.add_edge(e, entries[1 + i])

    try:
        assert list(network.sort()) is None, "Sort returned - expected CyclicGraphError"
    except CyclicGraphError:
        pass
