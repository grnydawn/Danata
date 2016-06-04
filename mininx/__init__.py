"""
MiniNX
========

    MiniNX (NX) is a Minimal version of MiniNX Python package for the creation, manipulation, and
    study of the structure, dynamics, and functions of complex networks
"""

from __future__ import absolute_import

import sys
if sys.version_info[:2] < (2, 7):
    m = "Python 2.7 or later is required for MiniNX (%d.%d detected)."
    raise ImportError(m % sys.version_info[:2])
del sys

# These are import orderwise
from mininx.exception import *
import mininx.utils

import mininx.classes
from mininx.classes import *

import mininx.convert
from mininx.convert import *

import mininx.tree
from mininx.tree import *
