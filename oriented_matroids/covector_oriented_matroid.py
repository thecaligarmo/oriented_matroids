r"""
Oriented matroid with covector axioms
---------------------------------------

This implements an oriented matroid using the covector axioms.

AUTHORS:

- Aram Dermenjian (2019-07-12): Initial version
"""

##############################################################################
#       Copyright (C) 2019 Aram Dermenjian <aram.dermenjian at gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
##############################################################################

from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from oriented_matroids.oriented_matroids_category import OrientedMatroids
from oriented_matroids.signed_vector_element import SignedVectorElement

import copy


class CovectorOrientedMatroid(UniqueRepresentation, Parent):
    r"""
    An oriented matroid implemented using covector axioms.

    According to  Definition 3.7.1 in [BLSWZ1999]_ a *covector* of an oriented
    matroid is any composition of cocircuits.

    This implements an oriented matroid using the covector axioms. For this
    let `\mathcal{L}` be a set of covectors and `E` a ground set. Then
    a pair `M = (E,\mathcal{L})` is an oriented matroid using the covectors
    axioms if (see Theorem 4.1.1 in [BLSWZ1999]_):

        - `0 \in \mathcal{L}`
        - `X \in \mathcal{L}` implies `-X \in \mathcal{L}`
        - For all `X,Y \in \mathcal{L}`, `X \circ Y \in \mathcal{L}`
        - For all `X,Y \in \mathcal{L}` and `e \in S(X,Y)` there exists a
          `Z \in \mathcal{L}` such that `Z(e) = 0` and
          `Z(f) = (X \circ Y)(f) = (Y \circ X)(f)` for all `f \notin S(X,Y)`.

    INPUT:

    - ``data`` -- a tuple containing SignedVectorElement elements or data
      that can be used to construct :class:`SignedVectorElement` elements
    - ``goundset`` -- (default: ``None``) is the groundset for the
      data. If not provided, we grab the data from the signed subsets.

    EXAMPLES::

        sage: from oriented_matroids import OrientedMatroid
        sage: M = OrientedMatroid([[1],[-1],[0]], groundset=['e'], key='covector')
        sage: M
        Covector oriented matroid of rank 1
        sage: M.groundset()
        ('e',)

        sage: C = [ [1,1,1], [1,1,0],[1,1,-1],[1,0,-1],[1,-1,-1],[0,-1,-1],
        ....: [-1,-1,-1],[0,1,1],[-1,1,1],[-1,0,1],[-1,-1,1],[-1,-1,0],[0,0,0]]
        sage: M = OrientedMatroid(C, key='covector'); M
        Covector oriented matroid of rank 2
        sage: M.groundset()
        (0, 1, 2)
        sage: gs = ['h1', 'h2', 'h3']
        sage: M = OrientedMatroid(C, key='covector', groundset=gs)
        sage: M.groundset()
        ('h1', 'h2', 'h3')


    .. SEEALSO::

        :class:`oriented_matroids.oriented_matroid.OrientedMatroid`
        :class:`oriented_matroids.oriented_matroids_category.OrientedMatroids`
    """

    Element = SignedVectorElement

    @staticmethod
    def __classcall__(cls, data, groundset=None, category=None):
        """
        Normalize arguments and set class.
        """
        if category is None:
            category = OrientedMatroids()
        return super(CovectorOrientedMatroid, cls) \
            .__classcall__(cls, data, groundset=groundset, category=category)

    def __init__(self, data, groundset=None, category=None):
        """
        Initialize ``self``
        """
        Parent.__init__(self, category=category)

        # Set up our covectors
        covectors = []
        for d in data:
            # Ensure we're using the right type.
            covectors.append(self.element_class(self,
                                                data=d,
                                                groundset=groundset))
        # If our groundset is none, make sure the groundsets are the same for
        # all elements
        if groundset is None and len(covectors) > 0:
            groundset = covectors[0].groundset()
            for X in covectors:
                if X.groundset() != groundset:
                    raise ValueError("Groundsets must be the same")

        self._covectors = covectors
        self._elements = covectors

        if groundset is None:
            self._groundset = groundset
        else:
            self._groundset = tuple(groundset)

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        try:
            rep = "Covector oriented matroid of rank {}".format(self.rank())
        except ValueError:
            rep = "Covector oriented matroid"
        return rep

    def is_valid(self):
        """
        Returns whether our covectors satisfy the covector axioms.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: M = OrientedMatroid([[1],[-1],[0]], groundset=['e'], key='covector')
            sage: M
            Covector oriented matroid of rank 1

            sage: C2 = [ [0,0],[1,1]]
            sage: OrientedMatroid(C2, key='covector')
            Traceback (most recent call last):
            ...
            ValueError: Every element needs an opposite

            sage: C3 = [[1,1],[-1,-1],[0,1],[1,0],[-1,0],[0,-1]]
            sage: OrientedMatroid(C3, key='covector')
            Traceback (most recent call last):
            ...
            ValueError: Composition must be in vectors


            sage: C4 = [ [0,0],[1,1],[-1,-1],[1,-1],[-1,1]]
            sage: M = OrientedMatroid(C4, key='covector'); M
            Traceback (most recent call last):
            ...
            ValueError: weak elimination failed

        """
        covectors = self.covectors()

        zero_found = False
        for X in covectors:
            # Axiom 1: Make sure empty is not present
            if X.is_zero():
                zero_found = True
            # Axiom 2: Make sure negative exists
            if -X not in covectors:
                raise ValueError("Every element needs an opposite")
            for Y in covectors:
                # Axiom 3: Closed under composition
                if X.composition(Y) not in covectors:
                    raise ValueError("Composition must be in vectors")
                # Axiom 4: Weak elimination axiom
                E = X.separation_set(Y)
                ze = set(self.groundset()).difference(E)
                xy = X.composition(Y)
                for e in E:
                    found = False
                    for Z in covectors:
                        if found:
                            break
                        if Z(e) == 0:
                            found = True
                            for f in ze:
                                if Z(f) != xy(f):
                                    found = False
                    if not found:
                        raise ValueError("weak elimination failed")

        if not zero_found:
            raise ValueError("All zero covector is required")

        return True

    def matroid(self):
        r"""
        Returns the underlying matroid.

        Given a covector oriented matroid, the *underlying matroid* is the
        (flat) matroid whose collection of flats is given by the set of
        zeroes of all signed vectors.

        *Note* that matroids as defined through flats are not defined in sage
        version 9.2 and therefore it must be translated to another one of the
        definitions.

        Instead, we order our flats by inclusion; giving us a rank function and
        use the rank function definition of matroid.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: C = [ [1,1,1], [1,1,0],[1,1,-1],[1,0,-1],[1,-1,-1],[0,-1,-1],
            ....: [-1,-1,-1],[0,1,1],[-1,1,1],[-1,0,1],[-1,-1,1],[-1,-1,0],
            ....: [0,0,0]]
            sage: M = OrientedMatroid(C, key='covector')
            sage: M.matroid()
            Matroid of rank 2 on 3 elements


        """
        from sage.matroids.constructor import Matroid
        from sage.combinat.posets.posets import Poset
        flats = list(set([frozenset(X.zeroes()) for X in self.elements()]))
        inc = lambda a,b: a.issubset(b)
        rf = Poset((flats, inc)).rank_function()
        return Matroid(groundset=self.groundset(), rank_function=rf)
