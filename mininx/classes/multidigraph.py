#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from copy import deepcopy
import mininx as nx
from mininx.classes.graph import Graph  # for doctests
from mininx.classes.digraph import DiGraph
from mininx.classes.multigraph import MultiGraph
from mininx.exception import MiniNXError

class MultiDiGraph(MultiGraph,DiGraph):
    # node_dict_factory=dict    # already assigned in Graph
    # adjlist_dict_factory=dict
    edge_key_dict_factory = dict
    # edge_attr_dict_factory=dict

    def __init__(self, data=None, **attr):
        self.edge_key_dict_factory = self.edge_key_dict_factory
        DiGraph.__init__(self, data, **attr)

    def add_edge(self, u, v, key=None, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise MiniNXError(
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        if u not in self.succ:
            self.succ[u] = self.adjlist_dict_factory()
            self.pred[u] = self.adjlist_dict_factory()
            self.node[u] = {}
        if v not in self.succ:
            self.succ[v] = self.adjlist_dict_factory()
            self.pred[v] = self.adjlist_dict_factory()
            self.node[v] = {}
        if v in self.succ[u]:
            keydict = self.adj[u][v]
            if key is None:
                # find a unique integer key
                # other methods might be better here?
                key = len(keydict)
                while key in keydict:
                    key += 1
            datadict = keydict.get(key, self.edge_key_dict_factory())
            datadict.update(attr_dict)
            keydict[key] = datadict
        else:
            # selfloops work this way without special treatment
            if key is None:
                key = 0
            datadict = self.edge_attr_dict_factory()
            datadict.update(attr_dict)
            keydict = self.edge_key_dict_factory()
            keydict[key] = datadict
            self.succ[u][v] = keydict
            self.pred[v][u] = keydict

    def remove_edge(self, u, v, key=None):
        try:
            d = self.adj[u][v]
        except (KeyError):
            raise MiniNXError(
                "The edge %s-%s is not in the graph." % (u, v))
        # remove the edge with specified data
        if key is None:
            d.popitem()
        else:
            try:
                del d[key]
            except (KeyError):
                raise MiniNXError(
                "The edge %s-%s with key %s is not in the graph." % (u, v, key))
        if len(d) == 0:
            # remove the key entries if last edge
            del self.succ[u][v]
            del self.pred[v][u]

    def edges(self, nbunch=None, data=False, keys=False, default=None):
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data is True:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key, ddict in keydict.items():
                        yield (n, nbr, key, ddict) if keys else (n, nbr, ddict)
        elif data is not False:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key, ddict in keydict.items():
                        d = ddict[data] if data in ddict else default
                        yield (n, nbr, key, d) if keys else (n, nbr, d)
        else:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key in keydict:
                        yield (n, nbr, key) if keys else (n, nbr)

    # alias out_edges to edges
    out_edges = edges

    def in_edges(self, nbunch=None, data=False, keys=False):
        if nbunch is None:
            nodes_nbrs = self.pred.items()
        else:
            nodes_nbrs = ((n, self.pred[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key, data in keydict.items():
                        if keys:
                            yield (nbr, n, key, data)
                        else:
                            yield (nbr, n, data)
        else:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    for key, data in keydict.items():
                        if keys:
                            yield (nbr, n, key)
                        else:
                            yield (nbr, n)


    def degree(self, nbunch=None, weight=None):
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            succ = self.succ[nbunch]
            pred = self.pred[nbunch]
            if weight is None:
                indeg = sum([len(data) for data in pred.values()])
                outdeg = sum([len(data) for data in succ.values()])
                return indeg + outdeg
            s = (sum(sum(data.get(weight, 1) for data in keydict.values())
                for keydict in succ.values())) + (sum(sum(data.get(weight, 1)
                for data in keydict.values()) for keydict in pred.values()))
            return s

        if nbunch is None:
            nodes_nbrs = ( (n, succ, self.pred[n])
                    for n,succ in self.succ.items() )
        else:
            nodes_nbrs = ( (n, self.succ[n], self.pred[n])
                    for n in self.nbunch_iter(nbunch))

        if weight is None:
            def d_iter():
                for n, succ, pred in nodes_nbrs:
                    indeg = sum([len(data) for data in pred.values()])
                    outdeg = sum([len(data) for data in succ.values()])
                    yield (n, indeg + outdeg)
        else:
            # edge weighted graph - degree is sum of nbr edge weights
            def d_iter():
                for n, succ, pred in nodes_nbrs:
                    deg = sum([d.get(weight, 1)
                               for data in pred.values()
                               for d in data.values()])
                    deg += sum([d.get(weight, 1)
                               for data in succ.values()
                               for d in data.values()])
                    yield (n, deg)
        return d_iter()

    def in_degree(self, nbunch=None, weight=None):
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            pred = self.pred[nbunch]
            if weight is None:
                return sum(len(data) for data in pred.values())
            return (sum(sum(data.get(weight,1) for data in keydict.values())
                           for keydict in pred.values()))
        if nbunch is None:
            nodes_nbrs = self.pred.items()
        else:
            nodes_nbrs = ((n, self.pred[n]) for n in self.nbunch_iter(nbunch))

        if weight is None:
            def d_iter():
                for n, nbrs in nodes_nbrs:
                    yield (n, sum([len(data) for data in nbrs.values()]))
        else:
            # edge weighted graph - degree is sum of nbr edge weights
            def d_iter():
                for n, pred in nodes_nbrs:
                    deg = sum([d.get(weight, 1)
                               for data in pred.values()
                               for d in data.values()])
                    yield (n, deg)
        return d_iter()

    def out_degree(self, nbunch=None, weight=None):
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            succ = self.succ[nbunch]
            if weight is None:
               return sum(len(data) for data in succ.values())
            return (sum(sum(data.get(weight,1) for data in keydict.values())
                           for keydict in succ.values()))
        if nbunch is None:
            nodes_nbrs = self.succ.items()
        else:
            nodes_nbrs = ((n, self.succ[n]) for n in self.nbunch_iter(nbunch))

        if weight is None:
            def d_iter():
                for n, nbrs in nodes_nbrs:
                    yield (n, sum([len(data) for data in nbrs.values()]))
        else:
            def d_iter():
                for n, succ in nodes_nbrs:
                    deg = sum([d.get(weight, 1)
                               for data in succ.values()
                               for d in data.values()])
                    yield (n, deg)
        return d_iter()

    def is_multigraph(self):
        return True

    def is_directed(self):
        return True

    def to_directed(self):
        return deepcopy(self)

    def to_undirected(self, reciprocal=False):
        H = MultiGraph()
        H.name = self.name
        H.add_nodes_from(self)
        if reciprocal is True:
            H.add_edges_from((u, v, key, deepcopy(data))
                            for u, nbrs in self.adjacency()
                            for v, keydict in nbrs.items()
                            for key, data in keydict.items()
                            if self.has_edge(v, u, key))
        else:
            H.add_edges_from((u, v, key, deepcopy(data))
                            for u, nbrs in self.adjacency()
                            for v, keydict in nbrs.items()
                            for key, data in keydict.items())
        H.graph = deepcopy(self.graph)
        H.node = deepcopy(self.node)
        return H

    def subgraph(self, nbunch):
        bunch = self.nbunch_iter(nbunch)
        # create new graph and copy subgraph into it
        H = self.__class__()
        # copy node and attribute dictionaries
        for n in bunch:
            H.node[n] = self.node[n]
        # namespace shortcuts for speed
        H_succ = H.succ
        H_pred = H.pred
        self_succ = self.succ
        self_pred = self.pred
        # add nodes
        for n in H:
            H_succ[n] = H.adjlist_dict_factory()
            H_pred[n] = H.adjlist_dict_factory()
        # add edges
        for u in H_succ:
            Hnbrs = H_succ[u]
            for v, edgedict in self_succ[u].items():
                if v in H_succ:
                    # add both representations of edge: u-v and v-u
                    # they share the same edgedict
                    ed = edgedict.copy()
                    Hnbrs[v] = ed
                    H_pred[v][u] = ed
        H.graph = self.graph
        return H

    def edge_subgraph(self, edges):
        H = self.__class__()
        succ = self.succ
        # Filter out edges that don't correspond to nodes in the graph.
        def is_in_graph(u, v, k):
            return u in succ and v in succ[u] and k in succ[u][v]
        edges = (e for e in edges if is_in_graph(*e))
        for u, v, k in edges:
            # Copy the node attributes if they haven't been copied
            # already.
            if u not in H.node:
                H.node[u] = self.node[u]
            if v not in H.node:
                H.node[v] = self.node[v]
            # Create an entry in the successors and predecessors
            # dictionary for the nodes u and v if they don't exist yet.
            if u not in H.succ:
                H.succ[u] = H.adjlist_dict_factory()
            if v not in H.pred:
                H.pred[v] = H.adjlist_dict_factory()
            # Create an entry in the edge dictionary for the edges (u,
            # v) and (v, u) if the don't exist yet.
            if v not in H.succ[u]:
                H.succ[u][v] = H.edge_key_dict_factory()
            if u not in H.pred[v]:
                H.pred[v][u] = H.edge_key_dict_factory()
            # Copy the edge attributes.
            H.edge[u][v][k] = self.edge[u][v][k]
            H.pred[v][u][k] = self.pred[v][u][k]
        H.graph = self.graph
        return H

    def reverse(self, copy=True):
        if copy:
            H = self.__class__(name="Reverse of (%s)"%self.name)
            H.add_nodes_from(self)
            H.add_edges_from((v, u, k, deepcopy(d)) for u, v, k, d
                              in self.edges(keys=True, data=True))
            H.graph = deepcopy(self.graph)
            H.node = deepcopy(self.node)
        else:
            self.pred, self.succ = self.succ, self.pred
            self.adj = self.succ
            H = self
        return H
