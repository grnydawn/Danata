# -*- coding: utf-8 -*-

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#

class MiniNXException(Exception):
    """Base class for exceptions in MiniNX."""

class MiniNXError(MiniNXException):
    """Exception for a serious error in MiniNX"""

class MiniNXPointlessConcept(MiniNXException):
    """Harary, F. and Read, R. "Is the Null Graph a Pointless Concept?"
In Graphs and Combinatorics Conference, George Washington University.
New York: Springer-Verlag, 1973.
"""

class MiniNXAlgorithmError(MiniNXException):
    """Exception for unexpected termination of algorithms."""

class MiniNXUnfeasible(MiniNXAlgorithmError):
    """Exception raised by algorithms trying to solve a problem
    instance that has no feasible solution."""

class MiniNXNoPath(MiniNXUnfeasible):
    """Exception for algorithms that should return a path when running
    on graphs where such a path does not exist."""

class MiniNXNoCycle(MiniNXUnfeasible):
    """Exception for algorithms that should return a cycle when running
    on graphs where such a cycle does not exist."""

class MiniNXUnbounded(MiniNXAlgorithmError):
    """Exception raised by algorithms trying to solve a maximization
    or a minimization problem instance that is unbounded."""

class MiniNXNotImplemented(MiniNXException):
    """Exception raised by algorithms not implemented for a type of graph."""

class NodeNotFound(MiniNXException):
    """Exception raised if requested node is not present in the graph"""
