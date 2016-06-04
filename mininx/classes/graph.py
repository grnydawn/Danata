class Graph(object):
    node_dict_factory = dict
    adjlist_dict_factory = dict
    edge_attr_dict_factory = dict

    def __init__(self, data=None, **attr):
        self.node_dict_factory = ndf = self.node_dict_factory
        self.adjlist_dict_factory = self.adjlist_dict_factory
        self.edge_attr_dict_factory = self.edge_attr_dict_factory

        self.graph = {}   # dictionary for graph attributes
        self.node = ndf()  # empty node attribute dict
        self.adj = ndf()  # empty adjacency dict
        # attempt to load graph with data
        if data is not None:
            convert.to_networkx_graph(data, create_using=self)
        # load graph attributes (must be after convert)
        self.graph.update(attr)
        self.edge = self.adj

    @property
    def name(self):
        return self.graph.get('name', '')

    @name.setter
    def name(self, s):
        self.graph['name'] = s

    def __str__(self):
        return self.name

    def __iter__(self):
        return iter(self.node)

    def __contains__(self, n):
        try:
            return n in self.node
        except TypeError:
            return False

    def __len__(self):
        return len(self.node)

    def __getitem__(self, n):
        return self.adj[n]

    def add_node(self, n, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise MiniNXError(
                    "The attr_dict argument must be a dictionary.")
        if n not in self.node:
            self.adj[n] = self.adjlist_dict_factory()
            self.node[n] = attr_dict
        else:  # update attr even if node already exists
            self.node[n].update(attr_dict)

    def add_nodes_from(self, nodes, **attr):
        for n in nodes:
            # keep all this inside try/except because
            # CPython throws TypeError on n not in self.node,
            # while pre-2.7.5 ironpython throws on self.adj[n]
            try:
                if n not in self.node:
                    self.adj[n] = self.adjlist_dict_factory()
                    self.node[n] = attr.copy()
                else:
                    self.node[n].update(attr)
            except TypeError:
                nn, ndict = n
                if nn not in self.node:
                    self.adj[nn] = self.adjlist_dict_factory()
                    newdict = attr.copy()
                    newdict.update(ndict)
                    self.node[nn] = newdict
                else:
                    olddict = self.node[nn]
                    olddict.update(attr)
                    olddict.update(ndict)

    def remove_node(self, n):
        adj = self.adj
        try:
            nbrs = list(adj[n].keys())  # keys handles self-loops (allow mutation later)
            del self.node[n]
        except KeyError:  # MiniNXError if n not in self
            raise MiniNXError("The node %s is not in the graph." % (n,))
        for u in nbrs:
            del adj[u][n]   # remove all edges n-u in graph
        del adj[n]          # now remove node

    def remove_nodes_from(self, nodes):
        adj = self.adj
        for n in nodes:
            try:
                del self.node[n]
                for u in list(adj[n].keys()):   # keys() handles self-loops
                    del adj[u][n]  # (allows mutation of dict in loop)
                del adj[n]
            except KeyError:
                pass

    def nodes(self, data=False, default=None):
        if data is True:
            for n, ddict in self.node.items():
                yield (n, ddict)
        elif data is not False:
            for n, ddict in self.node.items():
                d = ddict[data] if data in ddict else default
                yield (n, d)
        else:
            for n in self.node:
                yield n

    def number_of_nodes(self):
        return len(self.node)

    def order(self):
        return len(self.node)

    def has_node(self, n):
        try:
            return n in self.node
        except TypeError:
            return False

    def add_edge(self, u, v, attr_dict=None, **attr):
        # set up attribute dictionary
        if attr_dict is None:
            attr_dict = attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise MiniNXError(
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        if u not in self.node:
            self.adj[u] = self.adjlist_dict_factory()
            self.node[u] = {}
        if v not in self.node:
            self.adj[v] = self.adjlist_dict_factory()
            self.node[v] = {}
        # add the edge
        datadict = self.adj[u].get(v, self.edge_attr_dict_factory())
        datadict.update(attr_dict)
        self.adj[u][v] = datadict
        self.adj[v][u] = datadict

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
            if ne == 3:
                u, v, dd = e
            elif ne == 2:
                u, v = e
                dd = {}  # doesnt need edge_attr_dict_factory
            else:
                raise MiniNXError(
                    "Edge tuple %s must be a 2-tuple or 3-tuple." % (e,))
            if u not in self.node:
                self.adj[u] = self.adjlist_dict_factory()
                self.node[u] = {}
            if v not in self.node:
                self.adj[v] = self.adjlist_dict_factory()
                self.node[v] = {}
            datadict = self.adj[u].get(v, self.edge_attr_dict_factory())
            datadict.update(attr_dict)
            datadict.update(dd)
            self.adj[u][v] = datadict
            self.adj[v][u] = datadict

    def add_weighted_edges_from(self, ebunch, weight='weight', **attr):
        self.add_edges_from(((u, v, {weight: d}) for u, v, d in ebunch),
                            **attr)
    def remove_edge(self, u, v):
        try:
            del self.adj[u][v]
            if u != v:  # self-loop needs only one entry removed
                del self.adj[v][u]
        except KeyError:
            raise MiniNXError("The edge %s-%s is not in the graph" % (u, v))

    def remove_edges_from(self, ebunch):
        adj = self.adj
        for e in ebunch:
            u, v = e[:2]  # ignore edge data if present
            if u in adj and v in adj[u]:
                del adj[u][v]
                if u != v:  # self loop needs only one entry removed
                    del adj[v][u]

    def has_edge(self, u, v):
        try:
            return v in self.adj[u]
        except KeyError:
            return False

    def neighbors(self, n):
        try:
            return iter(self.adj[n])
        except KeyError:
            raise MiniNXError("The node %s is not in the graph." % (n,))

    def edges(self, nbunch=None, data=False, default=None):
        seen = {}     # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data is True:
            for n, nbrs in nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    if nbr not in seen:
                        yield (n, nbr, ddict)
                seen[n] = 1
        elif data is not False:
            for n, nbrs in nodes_nbrs:
                for nbr, ddict in nbrs.items():
                    if nbr not in seen:
                        d = ddict[data] if data in ddict else default
                        yield (n, nbr, d)
                seen[n] = 1
        else:  # data is False
            for n, nbrs in nodes_nbrs:
                for nbr in nbrs:
                    if nbr not in seen:
                        yield (n, nbr)
                seen[n] = 1
        del seen

    def get_edge_data(self, u, v, default=None):
        try:
            return self.adj[u][v]
        except KeyError:
            return default

    def adjacency(self):
        return iter(self.adj.items())

    def degree(self, nbunch=None, weight=None):
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            nbrs = self.adj[nbunch]
            if weight is None:
                return len(nbrs) + (1 if nbunch in nbrs else 0) # handle self-loops
            return sum(dd.get(weight, 1) for nbr,dd in nbrs.items()) +\
                    (nbrs[nbunch].get(weight, 1) if nbunch in nbrs else 0)

        if nbunch is None:
            nodes_nbrs = self.adj.items()
        else:
            nodes_nbrs = ((n, self.adj[n]) for n in self.nbunch_iter(nbunch))
        if weight is None:
            def d_iter():
                for n, nbrs in nodes_nbrs:
                    yield (n, len(nbrs) + (1 if n in nbrs else 0))  # return tuple (n,degree)
        else:
            def d_iter():
                for n, nbrs in nodes_nbrs:
                    yield (n, sum((nbrs[nbr].get(weight, 1) for nbr in nbrs)) +
                        (nbrs[n].get(weight, 1) if n in nbrs else 0))
        return d_iter()

    def clear(self):
        self.name = ''
        self.adj.clear()
        self.node.clear()
        self.graph.clear()

    def copy(self, with_data=True):
        if with_data:
            return deepcopy(self)
        return self.subgraph(self)

    def is_multigraph(self):
        """Return True if graph is a multigraph, False otherwise."""
        return False

    def is_directed(self):
        """Return True if graph is directed, False otherwise."""
        return False

    def to_directed(self):
        from mininx import DiGraph
        G = DiGraph()
        G.name = self.name
        G.add_nodes_from(self)
        G.add_edges_from(((u, v, deepcopy(data))
            for u, nbrs in self.adjacency()
            for v, data in nbrs.items()))
        G.graph = deepcopy(self.graph)
        G.node = deepcopy(self.node)
        return G

    def to_undirected(self):
        return deepcopy(self)

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
        # Note that changing this may affect the deep-ness of self.copy()
        for n in H.node:
            Hnbrs = H.adjlist_dict_factory()
            H_adj[n] = Hnbrs
            for nbr, d in self_adj[n].items():
                if nbr in H_adj:
                    # add both representations of edge: n-nbr and nbr-n
                    Hnbrs[nbr] = d
                    H_adj[nbr][n] = d
        H.graph = self.graph
        return H

    def edge_subgraph(self, edges):
        H = self.__class__()
        adj = self.adj
        # Filter out edges that don't correspond to nodes in the graph.
        edges = ((u, v) for u, v in edges if u in adj and v in adj[u])
        for u, v in edges:
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
            # Copy the edge attributes.
            H.edge[u][v] = self.edge[u][v]
            H.edge[v][u] = self.edge[v][u]
        H.graph = self.graph
        return H

    def nodes_with_selfloops(self):
        return (n for n, nbrs in self.adj.items() if n in nbrs)

    def selfloop_edges(self, data=False, default=None):
        if data is True:
            return ((n, n, nbrs[n])
                    for n, nbrs in self.adj.items() if n in nbrs)
        elif data is not False:
            return ((n, n, nbrs[n].get(data, default))
                    for n, nbrs in self.adj.items() if n in nbrs)
        else:
            return ((n, n)
                    for n, nbrs in self.adj.items() if n in nbrs)

    def number_of_selfloops(self):
        return sum(1 for _ in self.selfloop_edges())

    def size(self, weight=None):
        s = sum(d for v, d in self.degree(weight=weight))
        # If `weight` is None, the sum of the degrees is guaranteed to be
        # even, so we can perform integer division and hence return an
        # integer. Otherwise, the sum of the weighted degrees is not
        # guaranteed to be an integer, so we perform "real" division.
        return s // 2 if weight is None else s / 2

    def number_of_edges(self, u=None, v=None):
        if u is None: return int(self.size())
        if v in self.adj[u]:
            return 1
        else:
            return 0

    def nbunch_iter(self, nbunch=None):
        if nbunch is None:   # include all nodes via iterator
            bunch = iter(self.adj)
        elif nbunch in self:  # if nbunch is a single node
            bunch = iter([nbunch])
        else:                # if nbunch is a sequence of nodes
            def bunch_iter(nlist, adj):
                try:
                    for n in nlist:
                        if n in adj:
                            yield n
                except TypeError as e:
                    message = e.args[0]
                    # capture error for non-sequence/iterator nbunch.
                    if 'iter' in message:
                        raise MiniNXError(
                            "nbunch is not a node or a sequence of nodes.")
                    # capture error for unhashable node.
                    elif 'hashable' in message:
                        raise MiniNXError(
                            "Node {} in the sequence nbunch is not a valid node.".format(n))
                    else:
                        raise
            bunch = bunch_iter(nbunch, self.adj)
        return bunch
