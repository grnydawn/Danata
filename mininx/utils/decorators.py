
import mininx as nx
from decorator import decorator

__all__ = [
    'not_implemented_for' ]

def not_implemented_for(*graph_types):
    @decorator
    def _not_implemented_for(f,*args,**kwargs):
        graph = args[0]
        terms= {'directed':graph.is_directed(),
                'undirected':not graph.is_directed(),
                'multigraph':graph.is_multigraph(),
                'graph':not graph.is_multigraph()}
        match = True
        try:
            for t in graph_types:
                match = match and terms[t]
        except KeyError:
            raise KeyError('use one or more of ',
                           'directed, undirected, multigraph, graph')
        if match:
            raise nx.MiniNXNotImplemented('not implemented for %s type'%
                                            ' '.join(graph_types))
        else:
            return f(*args,**kwargs)
    return _not_implemented_for
