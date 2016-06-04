#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from copy import deepcopy
import mininx as nx
from mininx.classes.graph import Graph
from mininx import MiniNXError

class MultiGraph(Graph):
    # node_dict_factory=dict    # already assigned in Graph
    # adjlist_dict_factory=dict
    edge_key_dict_factory = dict
    # edge_attr_dict_factory=dict

    def __init__(self, data=None, **attr):
        self.edge_key_dict_factory = self.edge_key_dict_factory
        Graph.__init__(self, data, **attr)

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
        if u not in self.adj:
            self.adj[u] = self.adjlist_dict_factory()
            self.node[u] = {}
        if v not in self.adj:
            self.adj[v] = self.adjlist_dict_factory()
            self.node[v] = {}
        if v in self.adj[u]:
            keydict = self.adj[u][v]
            if key is None:
                # find a unique integer key
                # other methods might be better here?
                key = len(keydict)
                while key in keydict:
                    key += 1
            datadict = keydict.get(key, self.edge_attr_dict_factory())
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
            self.adj[u][v] = keydict
            self.adj[v][u] = keydict

    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise MiniNXError(
                    "The attr_dict argument must be a dictionary.")
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne == 4:
                u, v, key, dd = e
            elif ne == 3:
                u, v, dd = e
                key = None
            elif ne == 2:
                u, v = e
                dd = {}
                key = None
            else:
                raise MiniNXError(
                    "Edge tuple %s must be a 2-tuple, 3-tuple or 4-tuple." % (e,))
            ddd = {}
            ddd.update(attr_dict)
            ddd.update(dd)
            self.add_edge(u, v, key, ddd)

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
                    "The edge %s-%s with key %s is not in the graph." % (
                        u, v, key))
        if len(d) == 0:
            # remove the key entries if last edge
            del self.adj[u][v]
            if u!=v:  # check for selfloop
                del self.adj[v][u]

    def remove_edges_from(self, ebunch):
        for e in ebunch:
            try:
                self.remove_edge(*e[:3])
            except MiniNXError:
                pass

    def has_edge(self, u, v, key=None):
        try:
            if key is None:
                return v in self.adj[u]
            else:
                return key in self.adj[u][v]
        except KeyError:
            return False


    def edges(self, nbunch=None, data=False, keys=False, default=None):
        seen = {}     # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data is True:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key, ddict in keydict.items():
                            yield (n, nbr, key, ddict) if keys else (n, nbr, ddict)
                seen[n] = 1
        elif data is not False:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key, ddict in keydict.items():
                            d = ddict[data] if data in ddict else default
                            yield (n, nbr, key, d) if keys else (n, nbr, d)
                seen[n] = 1
        else:
            for n, nbrs in nodes_nbrs:
                for nbr, keydict in nbrs.items():
                    if nbr not in seen:
                        for key in keydict:
                            yield (n, nbr, key) if keys else (n, nbr)
                seen[n] = 1
        del seen


    def get_edge_data(self, u, v, key=None, default=None):
        try:
            if key is None:
                return self.adj[u][v]
            else:
                return self.adj[u][v][key]
        except KeyError:
            return default

    def degree(self, nbunch=None, weight=None):
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            nbrs = self.adj[nbunch]
            if weight is None:
                return sum([len(data) for data in nbrs.values()]) + (nbunch in nbrs and len(nbrs[nbunch]))
            deg = sum([d.get(weight, 1) for data in nbrs.values() for d in data.values()])
            if nbunch in nbrs:
                deg += sum([d.get(weight, 1) for key, d in nbrs[nbunch].items()])
            return deg
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))

        if weight is None:
            def d_iter():
                for n, nbrs in nodes_nbrs:
                    deg = sum([len(data) for data in nbrs.values()])
                    yield (n, deg + (n in nbrs and len(nbrs[n])))
        else:
            # edge weighted graph - degree is sum of nbr edge weights
            def d_iter():
                for n, nbrs in nodes_nbrs:
                    deg = sum([d.get(weight, 1)
                               for data in nbrs.values()
                               for d in data.values()])
                    if n in nbrs:
                        deg += sum([d.get(weight, 1)
                                    for key, d in nbrs[n].items()])
                    yield (n, deg)
        return d_iter()

    def is_multigraph(self):
        return True

    def is_directed(self):
        return False

    def to_directed(self):
        from mininx.classes.multidigraph import MultiDiGraph
        G = MultiDiGraph()
        G.add_nodes_from(self)
        G.add_edges_from((u, v, key, deepcopy(datadict))
                            for u, nbrs in self.adjacency()
                            for v, keydict in nbrs.items()
                            for key, datadict in keydict.items())
        G.graph = deepcopy(self.graph)
        G.node = deepcopy(self.node)
        return G

    def selfloop_edges(self, data=False, keys=False, default=None):
        if data is True:
            if keys:
                return ((n, n, k, d)
                        for n, nbrs in self.adj.items()
                        if n in nbrs for k, d in nbrs[n].items())
            else:
                return ((n, n, d)
                        for n, nbrs in self.adj.items()
                        if n in nbrs for d in nbrs[n].values())
        elif data is not False:
            if keys:
                return ((n, n, k, d.get(data, default))
                        for n, nbrs in self.adj.items()
                        if n in nbrs for k, d in nbrs[n].items())
            else:
                return ((n, n, d.get(data, default))
                        for n, nbrs in self.adj.items()
                        if n in nbrs for d in nbrs[n].values())
        else:
            if keys:
                return ((n, n, k)
                        for n, nbrs in self.adj.items()
                        if n in nbrs for k in nbrs[n].keys())
            else:
                return ((n, n)
                        for n, nbrs in self.adj.items()
                        if n in nbrs for d in nbrs[n].values())

    def number_of_edges(self, u=None, v=None):
        if u is None: return self.size()
        try:
            edgedata = self.adj[u][v]
        except KeyError:
            return 0  # no such edge
        return len(edgedata)

    def subgraph(self, nbunch):
        bunch = self.nbunch_iter(nbunch)
        # create new graph and copy subgraph into it
        H = self.__class__()
        # copy node and attribute dictionaries
        for n in bunch:
            H.node[n] = self.node[n]
        # namespace shortcuts for speed
        H_adj = H.adj
        self_adj = self.adj
        # add nodes and edges (undirected method)
        for n in H:
            Hnbrs = H.adjlist_dict_factory()
            H_adj[n] = Hnbrs
            for nbr, edgedict in self_adj[n].items():
                if nbr in H_adj:
                    # add both representations of edge: n-nbr and nbr-n
                    # they share the same edgedict
                    ed = edgedict.copy()
                    Hnbrs[nbr] = ed
                    H_adj[nbr][n] = ed
        H.graph = self.graph
        return H

    def edge_subgraph(self, edges):
        H = self.__class__()
        adj = self.adj
        # Filter out edges that don't correspond to nodes in the graph.
        def is_in_graph(u, v, k):
            return u in adj and v in adj[u] and k in adj[u][v]
        edges = (e for e in edges if is_in_graph(*e))
        for u, v, k in edges:
            # Copy the node attributes if they haven't been copied
            # already.
            if u not in H.node:
                H.node[u] = self.node[u]
            if v not in H.node:
                H.node[v] = self.node[v]
            # Create an entry in the adjacency dictionary for the
            # nodes u and v if they don't exist yet.
            if u not in H.adj:
                H.adj[u] = H.adjlist_dict_factory()
            if v not in H.adj:
                H.adj[v] = H.adjlist_dict_factory()
            # Create an entry in the edge dictionary for the edges (u,
            # v) and (v, u) if the don't exist yet.
            if v not in H.adj[u]:
                H.adj[u][v] = H.edge_key_dict_factory()
            if u not in H.adj[v]:
                H.adj[v][u] = H.edge_key_dict_factory()
            # Copy the edge attributes.
            H.edge[u][v][k] = self.edge[u][v][k]
            H.edge[v][u][k] = self.edge[v][u][k]
        H.graph = self.graph
        return H
