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
        sage: M = OrientedMatroid([[1],[-1],[0]], groundset=['e'],key='covector'); M
        Covector oriented matroid of rank 1
        sage: M.groundset()
        ('e',)

        sage: C = [ [1,1,1], [1,1,0],[1,1,-1],[1,0,-1],[1,-1,-1],[0,-1,-1],[-1,-1,-1],
        ....: [0,1,1],[-1,1,1],[-1,0,1],[-1,-1,1],[-1,-1,0],[0,0,0]]
        sage: M = OrientedMatroid(C, key='covector'); M
        Covector oriented matroid of rank 3
        sage: M.groundset()
        (0, 1, 2)
        sage: M = OrientedMatroid(C, key='covector',groundset=['h1','h2','h3']);
        sage: M.groundset()
        ('h1', 'h2', 'h3')


    .. SEEALSO::

        :class:`oriented_matroids.oriented_matroid.OrientedMatroid`
        :class:`oriented_matroids.oriented_matroids_category.OrientedMatroids`
    """
    Element = SignedVectorElement
    key = 'covector'

    @staticmethod
    def __classcall__(cls, data, groundset=None):
        """
        Normalize arguments and set class.
        """
        category = OrientedMatroids()
        return super(CovectorOrientedMatroid, cls).__classcall__(cls, data, groundset=groundset, category=category)

    def __init__(self,data, groundset=None, category=None):
        """
        Initialize ``self``
        """
        Parent.__init__(self, category=category)

        # Set up our covectors
        covectors = []
        for d in data:
            # Ensure we're using the right type.
            covectors.append(self.element_class(self,data=d, groundset=groundset))
        # If our groundset is none, make sure the groundsets are the same for all elements
        if groundset is None and len(covectors) > 0:
            groundset = covectors[0].groundset()
            for X in covectors:
                if X.groundset() != groundset:
                    raise ValueError("Groundsets must be the same")

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
        except:
            rep = "Covector oriented matroid"
        return rep

    def is_valid(self):
        """
        Returns whether our covectors satisfy the covector axioms.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: M = OrientedMatroid([[1],[-1],[0]], groundset=['e'],key='covector'); M
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
            raise ValueError("Empty set is required")

        return True

    def covectors(self):
        """
        Shorthand for :meth:`~oriented_matroids.oriented_matroids_category.OrientedMatroids.elements`
        """
        return self.elements()

    def matroid(self):
        r"""
        Return the matroid of a covector oriented matroid
        """

        from sage.matroids.constructor import Matroid
        from sage.matrix.constructor import matrix

        els = self.elements()
        mins = []
        for X in els:
            if not X.is_zero():
                tmp = True
                for Y in els:
                    if Y != X and not Y.is_zero() and Y.composition(X) == X:
                        tmp = False
                        break
                if tmp:
                    mins.append(X)
        
        return Matroid(matrix=matrix([v.to_list() for v in mins]),groundset=self.groundset())

    def face_poset(self, facade=False):
        r"""
        Returns the (big) face poset.

        The *(big) face poset* is the poset on covectors such that `X \leq Y`
        if and onlyif `S(X,Y) = \emptyset` and `\underline{Y} \subseteq \underline{X}`.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: C = [ [1,1,1], [1,1,0],[1,1,-1],[1,0,-1],[1,-1,-1],[0,-1,-1],[-1,-1,-1],
            ....: [0,1,1],[-1,1,1],[-1,0,1],[-1,-1,1],[-1,-1,0],[0,0,0]]
            sage: M = OrientedMatroid(C, key='covector')
            sage: M.face_poset()
            Finite poset containing 13 elements



        """
        from sage.combinat.posets.posets import Poset
        from sage.combinat.posets.lattices import MeetSemilattice
        els = self.covectors()
        rels = [ (Y,X) for X in els for Y in els if Y.is_conformal_with(X) and Y.support().issubset(X.support())]
        P = Poset((els, rels), cover_relations=False, facade=facade)
        return MeetSemilattice(P)

