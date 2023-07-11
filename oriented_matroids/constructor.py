# -*- coding: utf-8 -*-
r"""
Oriented matroids construction

Theory
======

Oriented matroids are ...

Built-in oriented matroids
==========================

...

Constructing oriented matroids
==============================

To define your own oriented matroid,...


AUTHORS:

- Aram Dermenjian (2019-07-12): initial version

"""

# *****************************************************************************
#       Copyright (C) 2019 Aram Dermenjian <aram.dermenjian at gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
# *****************************************************************************

from sage.geometry.hyperplane_arrangement.arrangement \
    import HyperplaneArrangementElement
from sage.geometry.triangulation.point_configuration \
    import PointConfiguration
from sage.graphs.digraph import DiGraph
from sage.structure.element import Matrix
import copy


def OrientedMatroid(data=None, groundset=None, key=None, **kwds):
    r"""
    Construct an oriented matroid.

    The implementation of the oriented matroid differentiates which
    axiom set that will be used.#

    INPUT:

    - ``groundset`` -- (default: ``None``) is the ground set that will be
      used for the oriented matroid.

    - ``data`` -- (default: ``None``) the data that will be used to define
      the oriented matroids. It can be one of the following:

      + Objects

          + Hyperplane Arrangement
          + Point Configuration
          + Digraph
          + Matrix (not yet implemented)

      + A list or tuple of

          + :class:`SignedSubsetElement`
          + :class:`SignedVectorElement`
          + A tuple with positive, negative, and zero sets.

    - ``key`` -- (default: ``None``) is the representation of the
      oriented matroid. It can be one of the following:

      + ``'covector'`` - uses covector axioms with covectors
      + ``'vector'`` - uses vector axioms with signed subsets
      + ``'circuit'`` - uses circuit axioms with signed subsets
      + ``None`` - try and guess key.

    Further options:


    EXAMPLES::

        sage: from oriented_matroids import OrientedMatroid

        sage: A = hyperplane_arrangements.braid(3)
        sage: M = OrientedMatroids(A); M
        Hyperplane arrangement oriented matroid of rank 2
        sage: M.groundset()
        (Hyperplane 0*t0 + t1 - t2 + 0,
         Hyperplane t0 - t1 + 0*t2 + 0,
         Hyperplane t0 + 0*t1 - t2 + 0)
        sage: M.elements()
        [(0,0,0),
         (0,1,1),
         (0,-1,-1),
         (1,0,1),
         (1,1,1),
         (1,-1,0),
         (1,-1,1),
         (1,-1,-1),
         (-1,0,-1),
         (-1,1,0),
         (-1,1,1),
         (-1,1,-1),
         (-1,-1,-1)]

        sage: D = DiGraph({'v1':{'v2':1,'v3':2,'v4':3},'v2':{'v3':4,'v4':5},'v3':{'v4':6}})
        sage: M = OrientedMatroid(D,key="circuit"); M
        Circuit oriented matroid of rank 3
        sage: len(M.circuits())
        14

        sage: PC = PointConfiguration([[1,0,0],[0,1,0],[0,0,1],[1/2,1/2,0],[0,1/2,1/2],[1/3,1/3,1/3]])
        sage: M = OrientedMatroid(PC); M
        Circuit oriented matroid of rank 3
        sage: M.matroid()
        Matroid of rank 3 on 6 elements with 16 bases

        sage: OrientedMatroid([[0]],key='covector')
        Covector oriented matroid of rank 0
        sage: OrientedMatroid([[0]],key='circuit')
        Traceback (most recent call last):
        ...
        ValueError: Empty set not allowed

    OUTPUT:

    An oriented matroid whose axioms are determined by the type.

    .. TODO::

        - Currently chirotopes are not implemented
        - We need a way to go from one type to another

    .. SEEALSO::

        :class:`oriented_matroids.oriented_matroids_category.OrientedMatroids`

    REFERENCES:

    For more information see [BLSWZ1999]_ .

    """

    # Instantiate oriented matroid
    OM = None

    # If we have a hyperplane arrangement we need to force the key to be an
    # arrangement,
    if isinstance(data, HyperplaneArrangementElement):
        if key != 'covector' and key is not None:
            raise ValueError(
                'Hyperplane arrangements are currently only implemented using covector axioms')
        key = 'real_hyperplane_arrangement'
    elif isinstance(data, PointConfiguration):
        if key != 'circuit' and key is not None:
            raise ValueError(
                'Point configurations are currently only implemented using circuit axioms')
        key = 'circuit'
        # PC circuits are given as (+, 0, -); and only half are given
        ci = [(C[0], C[2], C[1]) for C in data.circuits()]
        ci += [(C[2], C[0], C[1]) for C in data.circuits()]
        data = ci
    elif isinstance(data, DiGraph):
        if key != 'circuit' and key is not None:
            raise ValueError(
                'Digraphs are currently only implemented using circuit axioms')
        key = 'circuit'

        # we need to add negative edges in order to do all simple cycles
        digraph = copy.copy(data)
        edges = copy.copy(list(digraph.edges()))
        groundset = []
        if len(edges) != len(set(edges)):
            raise ValueError('Edge labels need to be unique')
        if None in digraph.edge_labels():
            raise ValueError('Edge labels must be set for all edges')

        # Add minus edges to properly get cycles
        for e in edges:
            digraph.add_edge(e[1], e[0], "NEG_"+str(e[2]))
            groundset.append(str(e[2]))
        # Each cycle defines a circuit
        data = []
        for c in digraph.all_cycles_iterator(simple=True):
            p = set([])
            n = set([])
            for e in range(len(c) - 1):
                e = str(digraph.edge_label(c[e], c[e+1]))
                if e.startswith('NEG_'):
                    n.add(e.strip('NEG_'))
                else:
                    p.add(e)
            # If an edge exists in both sets, then this is a false cycle.
            # This implies we have ee^-1 which is why it's false.
            # So we only add the true ones.
            if len(p.intersection(n)) == 0:
                data.append([p, n])
    elif isinstance(data, Matrix):
        if key != 'chirotope' and key is not None:
            raise ValueError(
                'Matrices are currently only implemented using chirotope axioms')
        key = 'chirotope'

    if key not in OrientedMatroids.keys:
        raise ValueError("invalid type key")

    # In the following cases, deep_tupler is used since we are using
    # UniqueRepresentation Which doesn't allow us to have non-hashable things.
    if key == "covector":
        from oriented_matroids.covector_oriented_matroid \
            import CovectorOrientedMatroid
        data = deep_tupler(data)
        if groundset is not None:
            groundset = deep_tupler(groundset)
        OM = CovectorOrientedMatroid(data, groundset=groundset)
    elif key == "circuit":
        from oriented_matroids.circuit_oriented_matroid \
            import CircuitOrientedMatroid
        data = deep_tupler(data)
        if groundset is not None:
            groundset = deep_tupler(groundset)
        OM = CircuitOrientedMatroid(data, groundset=groundset)
    elif key == "vector":
        from oriented_matroids.vector_oriented_matroid \
            import VectorOrientedMatroid
        data = deep_tupler(data)
        if groundset is not None:
            groundset = deep_tupler(groundset)
        OM = VectorOrientedMatroid(data, groundset=groundset)
    elif key == "real_hyperplane_arrangement":
        from oriented_matroids.real_hyperplane_arrangement_oriented_matroid \
            import RealHyperplaneArrangementOrientedMatroid
        A = copy.copy(data)
        if groundset is None:
            groundset = deep_tupler(A.hyperplanes())
        else:
            groundset = deep_tupler(groundset)
        OM = RealHyperplaneArrangementOrientedMatroid(A, groundset=groundset)

    if OM is None:
        raise NotImplementedError(
            "Oriented matroid of type {} is not implemented".format(key))

    if OM.is_valid():
        return OM

    raise ValueError("Oriented matroid is not valid")


def deep_tupler(obj):
    r"""
    changes a (nested) list or set into a (nested) tuple to be hashable
    """
    if isinstance(obj, list) or isinstance(obj, set):
        return tuple([deep_tupler(i) for i in obj])
    return obj