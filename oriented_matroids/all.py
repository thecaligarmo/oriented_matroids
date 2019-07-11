from __future__ import absolute_import

from sage.misc.lazy_import import lazy_import
lazy_import('sage.matroids.oriented_matroids','oriented_matroids_catalog','oriented_matroids')

from .oriented_matroid_category import OrientedMatroids
from .oriented_matroid import OrientedMatroid

