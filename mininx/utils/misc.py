# Authors:      Aric Hagberg (hagberg@lanl.gov),
#               Dan Schult(dschult@colgate.edu),
#               Ben Edwards(bedwards@cs.unm.edu)

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from itertools import tee, chain

def pairwise(iterable, cyclic=False):
    a, b = tee(iterable)
    first = next(b, None)
    if cyclic is True:
        return zip(a, chain(b, (first,)))
    return zip(a, b)
