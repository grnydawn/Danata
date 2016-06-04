#    Copyright (C) 2006-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import warnings
import mininx as nx

def _prep_create_using(create_using):
    if create_using is None:
        return nx.Graph()
    try:
        create_using.clear()
    except:
        raise TypeError("Input graph is not a networkx graph type")
    return create_using

def to_networkx_graph(data,create_using=None,multigraph_input=False):
    # NX graph
    if hasattr(data,"adj"):
        try:
            result= from_dict_of_dicts(data.adj,\
                    create_using=create_using,\
                    multigraph_input=data.is_multigraph())
            if hasattr(data,'graph'): # data.graph should be dict-like
                result.graph.update(data.graph)
            if hasattr(data,'node'): # data.node should be dict-like
                result.node.update( (n,dd.copy()) for n,dd in data.node.items() )
            return result
        except:
            raise nx.MiniNXError("Input is not a correct MiniNX graph.")

    # pygraphviz  agraph
    if hasattr(data,"is_strict"):
        try:
            return nx.nx_agraph.from_agraph(data,create_using=create_using)
        except:
            raise nx.MiniNXError("Input is not a correct pygraphviz graph.")

    # dict of dicts/lists
    if isinstance(data,dict):
        try:
            return from_dict_of_dicts(data,create_using=create_using,\
                    multigraph_input=multigraph_input)
        except:
            try:
                return from_dict_of_lists(data,create_using=create_using)
            except:
                raise TypeError("Input is not known type.")

    # list or generator of edges
    if (isinstance(data,list)
        or isinstance(data,tuple)
        or hasattr(data,'next')
        or hasattr(data, '__next__')):
        try:
            return from_edgelist(data,create_using=create_using)
        except:
            raise nx.MiniNXError("Input is not a valid edge list")

    # Pandas DataFrame
    try:
        import pandas as pd
        if isinstance(data, pd.DataFrame):
            try:
                return nx.from_pandas_dataframe(data, create_using=create_using)
            except:
                msg = "Input is not a correct Pandas DataFrame."
                raise nx.MiniNXError(msg)
    except ImportError:
        msg = 'pandas not found, skipping conversion test.'
        warnings.warn(msg, ImportWarning)

    # numpy matrix or ndarray
    try:
        import numpy
        if isinstance(data,numpy.matrix) or \
               isinstance(data,numpy.ndarray):
            try:
                return nx.from_numpy_matrix(data,create_using=create_using)
            except:
                raise nx.MiniNXError(\
                  "Input is not a correct numpy matrix or array.")
    except ImportError:
        warnings.warn('numpy not found, skipping conversion test.',
                      ImportWarning)

    # scipy sparse matrix - any format
    try:
        import scipy
        if hasattr(data,"format"):
            try:
                return nx.from_scipy_sparse_matrix(data,create_using=create_using)
            except:
                raise nx.MiniNXError(\
                      "Input is not a correct scipy sparse matrix type.")
    except ImportError:
        warnings.warn('scipy not found, skipping conversion test.',
                      ImportWarning)


    raise nx.MiniNXError(\
          "Input is not a known data type for conversion.")

    return


def convert_to_undirected(G):
    return G.to_undirected()


def convert_to_directed(G):
    return G.to_directed()


def to_dict_of_lists(G,nodelist=None):
    if nodelist is None:
        nodelist=G

    d = {}
    for n in nodelist:
        d[n]=[nbr for nbr in G.neighbors(n) if nbr in nodelist]
    return d

def from_dict_of_lists(d,create_using=None):
    G=_prep_create_using(create_using)
    G.add_nodes_from(d)
    if G.is_multigraph() and not G.is_directed():
        # a dict_of_lists can't show multiedges.  BUT for undirected graphs,
        # each edge shows up twice in the dict_of_lists.
        # So we need to treat this case separately.
        seen={}
        for node,nbrlist in d.items():
            for nbr in nbrlist:
                if nbr not in seen:
                    G.add_edge(node,nbr)
            seen[node]=1  # don't allow reverse edge to show up
    else:
        G.add_edges_from( ((node,nbr) for node,nbrlist in d.items()
                           for nbr in nbrlist) )
    return G


def to_dict_of_dicts(G,nodelist=None,edge_data=None):
    dod={}
    if nodelist is None:
        if edge_data is None:
            for u,nbrdict in G.adjacency():
                dod[u]=nbrdict.copy()
        else: # edge_data is not None
            for u,nbrdict in G.adjacency():
                dod[u]=dod.fromkeys(nbrdict, edge_data)
    else: # nodelist is not None
        if edge_data is None:
            for u in nodelist:
                dod[u]={}
                for v,data in ((v,data) for v,data in G[u].items() if v in nodelist):
                    dod[u][v]=data
        else: # nodelist and edge_data are not None
            for u in nodelist:
                dod[u]={}
                for v in ( v for v in G[u] if v in nodelist):
                    dod[u][v]=edge_data
    return dod

def from_dict_of_dicts(d,create_using=None,multigraph_input=False):
    G=_prep_create_using(create_using)
    G.add_nodes_from(d)
    # is dict a MultiGraph or MultiDiGraph?
    if multigraph_input:
        # make a copy of the list of edge data (but not the edge data)
        if G.is_directed():
            if G.is_multigraph():
                G.add_edges_from( (u,v,key,data)
                                  for u,nbrs in d.items()
                                  for v,datadict in nbrs.items()
                                  for key,data in datadict.items()
                                )
            else:
                G.add_edges_from( (u,v,data)
                                  for u,nbrs in d.items()
                                  for v,datadict in nbrs.items()
                                  for key,data in datadict.items()
                                )
        else: # Undirected
            if G.is_multigraph():
                seen=set()   # don't add both directions of undirected graph
                for u,nbrs in d.items():
                    for v,datadict in nbrs.items():
                        if (u,v) not in seen:
                            G.add_edges_from( (u,v,key,data)
                                               for key,data in datadict.items()
                                              )
                            seen.add((v,u))
            else:
                seen=set()   # don't add both directions of undirected graph
                for u,nbrs in d.items():
                    for v,datadict in nbrs.items():
                        if (u,v) not in seen:
                            G.add_edges_from( (u,v,data)
                                        for key,data in datadict.items() )
                            seen.add((v,u))

    else: # not a multigraph to multigraph transfer
        if G.is_multigraph() and not G.is_directed():
            # d can have both representations u-v, v-u in dict.  Only add one.
            # We don't need this check for digraphs since we add both directions,
            # or for Graph() since it is done implicitly (parallel edges not allowed)
            seen=set()
            for u,nbrs in d.items():
                for v,data in nbrs.items():
                    if (u,v) not in seen:
                        G.add_edge(u,v,attr_dict=data)
                    seen.add((v,u))
        else:
            G.add_edges_from( ( (u,v,data)
                                for u,nbrs in d.items()
                                for v,data in nbrs.items()) )
    return G

def to_edgelist(G,nodelist=None):
    if nodelist is None:
        return G.edges(data=True)
    else:
        return G.edges(nodelist,data=True)

def from_edgelist(edgelist,create_using=None):
    G=_prep_create_using(create_using)
    G.add_edges_from(edgelist)
    return G
