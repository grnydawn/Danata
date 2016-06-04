from mininx.classes.graph import Graph
from mininx.exception import MiniNXError
import mininx.convert as convert

class DiGraph(Graph):
    def __init__(self, data=None, **attr):
        self.node_dict_factory = ndf = self.node_dict_factory
        self.adjlist_dict_factory = self.adjlist_dict_factory
        self.edge_attr_dict_factory = self.edge_attr_dict_factory

        self.graph = {} # dictionary for graph attributes
        self.node = ndf() # dictionary for node attributes
        # We store two adjacency lists:
        # the  predecessors of node n are stored in the dict self.pred
        # the successors of node n are stored in the dict self.succ=self.adj
        self.adj = ndf()  # empty adjacency dictionary
        self.pred = ndf()  # predecessor
        self.succ = self.adj  # successor

        # attempt to load graph with data
        if data is not None:
            convert.to_networkx_graph(data,create_using=self)
        # load graph attributes (must be after convert)
        self.graph.update(attr)
        self.edge=self.adj

    def add_node(self, n, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise MiniNXError(\
                    "The attr_dict argument must be a dictionary.")
        if n not in self.succ:
            self.succ[n] = self.adjlist_dict_factory()
            self.pred[n] = self.adjlist_dict_factory()
            self.node[n] = attr_dict
        else: # update attr even if node already exists
            self.node[n].update(attr_dict)

    def add_nodes_from(self, nodes, **attr):
        for n in nodes:
            # keep all this inside try/except because
            # CPython throws TypeError on n not in self.succ,
            # while pre-2.7.5 ironpython throws on self.succ[n] 
            try:
                if n not in self.succ:
                    self.succ[n] = self.adjlist_dict_factory()
                    self.pred[n] = self.adjlist_dict_factory()
                    self.node[n] = attr.copy()
                else:
                    self.node[n].update(attr)
            except TypeError:
                nn,ndict = n
                if nn not in self.succ:
                    self.succ[nn] = self.adjlist_dict_factory()
                    self.pred[nn] = self.adjlist_dict_factory()
                    newdict = attr.copy()
                    newdict.update(ndict)
                    self.node[nn] = newdict
                else:
                    olddict = self.node[nn]
                    olddict.update(attr)
                    olddict.update(ndict)

    def remove_node(self, n):
        try:
            nbrs=self.succ[n]
            del self.node[n]
        except KeyError: # MiniNXError if n not in self
            raise MiniNXError("The node %s is not in the digraph."%(n,))
        for u in nbrs:
            del self.pred[u][n] # remove all edges n-u in digraph
        del self.succ[n]          # remove node from succ
        for u in self.pred[n]:
            del self.succ[u][n] # remove all edges n-u in digraph
        del self.pred[n]          # remove node from pred

    def remove_nodes_from(self, nbunch):
        for n in nbunch:
            try:
                succs=self.succ[n]
                del self.node[n]
                for u in succs:
                    del self.pred[u][n] # remove all edges n-u in digraph
                del self.succ[n]          # now remove node
                for u in self.pred[n]:
                    del self.succ[u][n] # remove all edges n-u in digraph
                del self.pred[n]          # now remove node
            except KeyError:
                pass # silent failure on remove

    def add_edge(self, u, v, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise MiniNXError(\
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        if u not in self.succ:
            self.succ[u]= self.adjlist_dict_factory()
            self.pred[u]= self.adjlist_dict_factory()
            self.node[u] = {}
        if v not in self.succ:
            self.succ[v]= self.adjlist_dict_factory()
            self.pred[v]= self.adjlist_dict_factory()
            self.node[v] = {}
        # add the edge
        datadict=self.adj[u].get(v,self.edge_attr_dict_factory())
        datadict.update(attr_dict)
        self.succ[u][v]=datadict
        self.pred[v][u]=datadict

    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise MiniNXError(\
                    "The attr_dict argument must be a dict.")
        # process ebunch
        for e in ebunch:
            ne = len(e)
            if ne==3:
                u,v,dd = e
                assert hasattr(dd,"update")
            elif ne==2:
                u,v = e
                dd = {}
            else:
                raise MiniNXError(\
                    "Edge tuple %s must be a 2-tuple or 3-tuple."%(e,))
            if u not in self.succ:
                self.succ[u] = self.adjlist_dict_factory()
                self.pred[u] = self.adjlist_dict_factory()
                self.node[u] = {}
            if v not in self.succ:
                self.succ[v] = self.adjlist_dict_factory()
                self.pred[v] = self.adjlist_dict_factory()
                self.node[v] = {}
            datadict=self.adj[u].get(v,self.edge_attr_dict_factory())
            datadict.update(attr_dict)
            datadict.update(dd)
            self.succ[u][v] = datadict
            self.pred[v][u] = datadict

    def remove_edge(self, u, v):
        try:
            del self.succ[u][v]
            del self.pred[v][u]
        except KeyError:
            raise MiniNXError("The edge %s-%s not in graph."%(u,v))

    def remove_edges_from(self, ebunch):
        for e in ebunch:
            (u,v)=e[:2]  # ignore edge data
            if u in self.succ and v in self.succ[u]:
                del self.succ[u][v]
                del self.pred[v][u]

    def has_successor(self, u, v):
        return (u in self.succ and v in self.succ[u])

    def has_predecessor(self, u, v):
        return (u in self.pred and v in self.pred[u])

    def successors(self,n):
        try:
            return iter(self.succ[n])
        except KeyError:
            raise MiniNXError("The node %s is not in the digraph."%(n,))

    def predecessors(self,n):
        try:
            return iter(self.pred[n])
        except KeyError:
            raise MiniNXError("The node %s is not in the digraph."%(n,))

    # digraph definitions
    neighbors = successors

    def edges(self, nbunch=None, data=False, default=None):
        if nbunch is None:
            nodes_nbrs=self.adj.items()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data is True:
            for n,nbrs in nodes_nbrs:
                for nbr,ddict in nbrs.items():
                    yield (n,nbr,ddict)
        elif data is not False:
            for n,nbrs in nodes_nbrs:
                for nbr,ddict in nbrs.items():
                    d=ddict[data] if data in ddict else default
                    yield (n,nbr,d)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr in nbrs:
                    yield (n,nbr)

    # alias out_edges to edges
    out_edges = edges

    def in_edges(self, nbunch=None, data=False):
        if nbunch is None:
            nodes_nbrs=self.pred.items()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,data in nbrs.items():
                    yield (nbr,n,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr in nbrs:
                    yield (nbr,n)


    def degree(self, nbunch=None, weight=None):
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            succ = self.succ[nbunch]
            pred = self.pred[nbunch]
            if weight is None:
                return len(succ) + len(pred)
            return sum(data.get(weight, 1) for data in succ.values()) + \
                   sum(data.get(weight, 1) for data in pred.values())

        if nbunch is None:
            nodes_nbrs=( (n,succs,self.pred[n]) for n,succs in self.succ.items())
        else:
            nodes_nbrs=( (n,self.succ[n],self.pred[n]) for n in self.nbunch_iter(nbunch))
        if weight is None:
            def d_iter():
                for n,succ,pred in nodes_nbrs:
                    yield (n,len(succ)+len(pred))
        else:
            def d_iter():
                for n,succ,pred in nodes_nbrs:
                    yield (n,
                      sum((data.get(weight,1) for data in succ.values()))+
                      sum((data.get(weight,1) for data in pred.values())))
        return d_iter()

    def in_degree(self, nbunch=None, weight=None):
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            pred = self.pred[nbunch]
            if weight is None:
                return len(pred)
            return sum(data.get(weight, 1) for data in pred.values())

        if nbunch is None:
            nodes_nbrs=self.pred.items()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))

        if weight is None:
            def d_iter():
                for n,nbrs in nodes_nbrs:
                    yield (n,len(nbrs))
        else:
        # edge weighted graph - degree is sum of edge weights
            def d_iter():
                for n,nbrs in nodes_nbrs:
                    yield (n, sum(data.get(weight,1) for data in nbrs.values()))
        return d_iter()


    def out_degree(self, nbunch=None, weight=None):
        # Test to see if nbunch is a single node, an iterator of nodes or
        # None(indicating all nodes). (nbunch in self) is True when nbunch
        # is a single node.
        if nbunch in self:
            succ = self.succ[nbunch]
            if weight is None:
                return len(succ)
            return sum(data.get(weight, 1) for data in succ.values())

        if nbunch is None:
            nodes_nbrs=self.succ.items()
        else:
            nodes_nbrs=((n,self.succ[n]) for n in self.nbunch_iter(nbunch))

        if weight is None:
            def d_iter():
                for n,nbrs in nodes_nbrs:
                    yield (n,len(nbrs))
        else:
        # edge weighted graph - degree is sum of edge weights
            def d_iter():
                for n,nbrs in nodes_nbrs:
                    yield (n, sum(data.get(weight,1) for data in nbrs.values()))
        return d_iter()

    def clear(self):
        self.succ.clear()
        self.pred.clear()
        self.node.clear()
        self.graph.clear()

    def is_multigraph(self):
        return False


    def is_directed(self):
        return True

    def to_directed(self):
        return deepcopy(self)

    def to_undirected(self, reciprocal=False):
        H=Graph()
        H.name=self.name
        H.add_nodes_from(self)
        if reciprocal is True:
            H.add_edges_from( (u,v,deepcopy(d))
                              for u,nbrs in self.adjacency()
                              for v,d in nbrs.items()
                              if v in self.pred[u])
        else:
            H.add_edges_from( (u,v,deepcopy(d))
                              for u,nbrs in self.adjacency()
                              for v,d in nbrs.items() )
        H.graph=deepcopy(self.graph)
        H.node=deepcopy(self.node)
        return H


    def reverse(self, copy=True):
        if copy:
            H = self.__class__(name="Reverse of (%s)"%self.name)
            H.add_nodes_from(self)
            H.add_edges_from( (v,u,deepcopy(d)) for u,v,d
                              in self.edges(data=True) )
            H.graph=deepcopy(self.graph)
            H.node=deepcopy(self.node)
        else:
            self.pred,self.succ=self.succ,self.pred
            self.adj=self.succ
            H=self
        return H


    def subgraph(self, nbunch):
        bunch = self.nbunch_iter(nbunch)
        # create new graph and copy subgraph into it
        H = self.__class__()
        # copy node and attribute dictionaries
        for n in bunch:
            H.node[n]=self.node[n]
        # namespace shortcuts for speed
        H_succ=H.succ
        H_pred=H.pred
        self_succ=self.succ
        # add nodes
        for n in H:
            H_succ[n]=H.adjlist_dict_factory()
            H_pred[n]=H.adjlist_dict_factory()
        # add edges
        for u in H_succ:
            Hnbrs=H_succ[u]
            for v,datadict in self_succ[u].items():
                if v in H_succ:
                    # add both representations of edge: u-v and v-u
                    Hnbrs[v]=datadict
                    H_pred[v][u]=datadict
        H.graph=self.graph
        return H

    def edge_subgraph(self, edges):
        H = self.__class__()
        succ = self.succ
        # Filter out edges that don't correspond to nodes in the graph.
        edges = ((u, v) for u, v in edges if u in succ and v in succ[u])
        for u, v in edges:
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
            # Copy the edge attributes.
            H.edge[u][v] = self.edge[u][v]
            H.pred[v][u] = self.pred[v][u]
        H.graph = self.graph
        return H
