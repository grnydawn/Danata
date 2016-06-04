#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Aric Hagberg <hagberg@lanl.gov>
#          Pieter Swart <swart@lanl.gov>
#          Dan Schult <dschult@colgate.edu>
"""Functional interface to graph methods and assorted utilities.
"""
from __future__ import division

from collections import Counter
from itertools import chain
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

import mininx as nx
from mininx.utils import not_implemented_for
from mininx.utils import pairwise

__all__ = ['nodes', 'edges', 'degree', 'degree_histogram', 'neighbors',
           'number_of_nodes', 'number_of_edges', 'density',
           'is_directed', 'info', 'freeze', 'is_frozen', 'subgraph',
           'add_star', 'add_path', 'add_cycle',
           'create_empty_copy', 'set_node_attributes',
           'get_node_attributes', 'set_edge_attributes',
           'get_edge_attributes', 'all_neighbors', 'non_neighbors',
           'non_edges', 'common_neighbors', 'is_weighted',
           'is_negatively_weighted', 'is_empty']

def nodes(G):
    return G.nodes()

def edges(G, nbunch=None):
    return G.edges(nbunch)

def degree(G, nbunch=None, weight=None):
    return G.degree(nbunch, weight)

def neighbors(G, n):
    return G.neighbors(n)

def number_of_nodes(G):
    return G.number_of_nodes()

def number_of_edges(G):
    return G.number_of_edges()

def density(G):
    n = number_of_nodes(G)
    m = number_of_edges(G)
    if m == 0 or n <= 1:
        return 0
    d = m / (n * (n - 1))
    if not G.is_directed():
        d *= 2
    return d

def degree_histogram(G):
    counts = Counter(d for n, d in G.degree())
    return [counts.get(i, 0) for i in range(max(counts) + 1)]

def is_directed(G):
    return G.is_directed()

def frozen(*args):
    raise nx.MiniNXError("Frozen graph can't be modified")

def freeze(G):
    G.add_node=frozen
    G.add_nodes_from=frozen
    G.remove_node=frozen
    G.remove_nodes_from=frozen
    G.add_edge=frozen
    G.add_edges_from=frozen
    G.remove_edge=frozen
    G.remove_edges_from=frozen
    G.clear=frozen
    G.frozen=True
    return G

def is_frozen(G):
    try:
        return G.frozen
    except AttributeError:
        return False


def add_star(G, nodes, **attr):
    nlist = iter(nodes)
    v = next(nlist)
    edges = ((v, n) for n in nlist)
    G.add_edges_from(edges, **attr)

def add_path(G, nodes, **attr):
    G.add_edges_from(pairwise(nodes), **attr)

def add_cycle(G, nodes, **attr):
    G.add_edges_from(pairwise(nodes, cyclic=True), **attr)

def subgraph(G, nbunch):
    return G.subgraph(nbunch)

def create_empty_copy(G, with_data=True):
    H = G.__class__()
    H.add_nodes_from(G.nodes(data=with_data))
    if with_data:
        H.graph.update(G.graph)
    return H

def info(G, n=None):
    info='' # append this all to a string
    if n is None:
        info+="Name: %s\n"%G.name
        type_name = [type(G).__name__]
        info+="Type: %s\n"%",".join(type_name)
        info+="Number of nodes: %d\n"%G.number_of_nodes()
        info+="Number of edges: %d\n"%G.number_of_edges()
        nnodes=G.number_of_nodes()
        if len(G) > 0:
            if G.is_directed():
                info+="Average in degree: %8.4f\n"%\
                    (sum(d for n, d in G.in_degree())/float(nnodes))
                info+="Average out degree: %8.4f"%\
                    (sum(d for n, d in G.out_degree())/float(nnodes))
            else:
                s=sum(dict(G.degree()).values())
                info+="Average degree: %8.4f"%\
                    (float(s)/float(nnodes))

    else:
        if n not in G:
            raise nx.MiniNXError("node %s not in graph"%(n,))
        info+="Node % s has the following properties:\n"%n
        info+="Degree: %d\n"%G.degree(n)
        info+="Neighbors: "
        info+=' '.join(str(nbr) for nbr in G.neighbors(n))
    return info

def set_node_attributes(G, name, values):
    # Treat `value` as the attribute value for each node.
    if not isinstance(values, dict):
        values = dict(zip_longest(G, [], fillvalue=values))

    for node, value in values.items():
        G.node[node][name] = value

def get_node_attributes(G, name):
    return {n: d[name] for n, d in G.node.items() if name in d}

def set_edge_attributes(G, name, values):
    # Treat `value` as the attribute value for each node.
    if not isinstance(values, dict):
        if G.is_multigraph():
            edges = G.edges(keys=True)
        else:
            edges = G.edges()
        values = dict(zip_longest(edges, [], fillvalue=values))

    if G.is_multigraph():
        for (u, v, key), value in values.items():
            G[u][v][key][name] = value
    else:
        for (u, v), value in values.items():
            G[u][v][name] = value

def get_edge_attributes(G, name):
    if G.is_multigraph():
        edges = G.edges(keys=True, data=True)
    else:
        edges = G.edges(data=True)
    return {x[:-1]: x[-1][name] for x in edges if name in x[-1]}


def all_neighbors(graph, node):
    if graph.is_directed():
        values = chain(graph.predecessors(node), graph.successors(node))
    else:
        values = graph.neighbors(node)
    return values

def non_neighbors(graph, node):
    nbors = set(neighbors(graph, node)) | {node}
    return (nnode for nnode in graph if nnode not in nbors)

def non_edges(graph):
    if graph.is_directed():
        for u in graph:
            for v in non_neighbors(graph, u):
                yield (u, v)
    else:
        nodes = set(graph)
        while nodes:
            u = nodes.pop()
            for v in nodes - set(graph[u]):
                yield (u, v)

@not_implemented_for('directed')
def common_neighbors(G, u, v):
    if u not in G:
        raise nx.MiniNXError('u is not in the graph.')
    if v not in G:
        raise nx.MiniNXError('v is not in the graph.')

    # Return a generator explicitly instead of yielding so that the above
    # checks are executed eagerly.
    return (w for w in G[u] if w in G[v] and w not in (u, v))

def is_weighted(G, edge=None, weight='weight'):
    if edge is not None:
        data = G.get_edge_data(*edge)
        if data is None:
            msg = 'Edge {!r} does not exist.'.format(edge)
            raise nx.MiniNXError(msg)
        return weight in data

    if is_empty(G):
        # Special handling required since: all([]) == True
        return False

    return all(weight in data for u, v, data in G.edges(data=True))

def is_negatively_weighted(G, edge=None, weight='weight'):
    if edge is not None:
        data = G.get_edge_data(*edge)
        if data is None:
            msg = 'Edge {!r} does not exist.'.format(edge)
            raise nx.MiniNXError(msg)
        return weight in data and data[weight] < 0

    return any(weight in data and data[weight] < 0
               for u, v, data in G.edges(data=True))

def is_empty(G):
    return not any(G.adj.values())

