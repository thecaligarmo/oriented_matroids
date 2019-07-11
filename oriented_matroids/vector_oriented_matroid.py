r"""
Oriented matroid with vector axioms
-------------------------------------

This implements an oriented matroid using the vector axioms.

AUTHORS:

- Aram Dermenjian (2019-07-12): Initial version
"""

##############################################################################
#       Copyright (C) 2018 Aram Dermenjian <aram.dermenjian at gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
##############################################################################

from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from oriented_matroids import OrientedMatroids
from oriented_matroids.signed_vector_element import SignedVectorElement


class VectorOrientedMatroid(UniqueRepresentation, Parent):
    r"""
    An oriented matroid implemented using vector axioms.

    This implements an oriented matroid using the vectors axioms. For this
    let `\mathcal{V}` be a set of signed subsets and `E` a ground set. Then
    a pair `M = (E,\mathcal{V})` is an oriented matroid using the vector
    axioms if (see Theorem 3.7.5 and Corollary 3.7.9 in [BLSWZ1999]_):

        - `\emptyset \in \mathcal{V}`
        - `\mathcal{V} = -\mathcal{V}`
        - For all `X,Y \in \mathcal{V}`, `X \circ Y \in \mathcal{V}`
        - For all `X,Y \in \mathcal{V}` and `e \in X^+ \cap Y^-` there exists
          a `Z \in \mathcal{V}` such that
          `Z^+ \subseteq (X^+ \cup Y^+) \backslash \left\{e\right\}` and
          `Z^- \subseteq (X^- \cup Y^-) \backslash \left\{e\right\}` and
          `(X \backslash Y) \cup (Y \backslash X) \cup (X^+ \cap Y^+) \cup (X^- \cap Y^-) \subseteq Z`.


    INPUT:

    - ``data`` -- a tuple containing SigneVectorElement elements or data
      that can be used to construct :class:`SignedVectorElement` elements
    - ``goundset`` -- (default: ``None``) is the groundset for the
      data. If not provided, we grab the data from the signed subsets.

    EXAMPLES::

        sage: from oriented_matroids import OrientedMatroid
        sage: M = OrientedMatroid([[1],[-1],[0]], key='vector'); M
        Vector Oriented Matroid of rank 1
        sage: M.groundset()
        [0]
        sage: M = OrientedMatroid([[1],[-1],[0]], key='vector', groundset=['e']); M
        Vector Oriented Matroid of rank 1
        sage: M.groundset()
        ['e']


    .. SEEALSO::

        - :class:`oriented_matroids.oriented_matroid.OrientedMatroid`
        - :class:`oriented_matroids.oriented_matroids_category.OrientedMatroids`
    """
    Element = SignedVectorElement

    @staticmethod
    def __classcall__(cls, data, groundset = None):
        """
        Normalize arguments and set class.
        """
        category = OrientedMatroids()
        return super(VectorOrientedMatroid, cls).__classcall__(cls, data, groundset = groundset, category=category)

    def __init__(self,data, groundset=None,category=None):
        """
        Initialize ``self``.
        """
        Parent.__init__(self,category = category)

        # Set up our vectors
        vectors = []
        for d in data:
            # Use the appropriate element
            vectors.append(self.element_class(self,data=d, groundset=groundset))

        # If our groundset is none, make sure the groundsets are the same for all elements
        if groundset is None:
            groundset = vectors[0].groundset()
            for X in vectors:
                if X.groundset() != groundset:
                    raise ValueError("Groundsets must be the same")

        self._elements = vectors
        self._groundset = list(groundset)


    def is_valid(self):
        """
        Returns whether our circuits satisfy the circuit axioms.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: V2 = [[1,1]]
            sage: OrientedMatroid(V2, key='vector')
            Traceback (most recent call last):
            ...
            ValueError: Every element needs an opposite
            
            sage: V3 = [[1,1],[-1,-1],[0,-1],[0,1],[-1,0],[1,0]]
            sage: OrientedMatroid(V3, key='vector')
            Traceback (most recent call last):
            ...
            ValueError: Composition must be in vectors
            
            sage: V4 = [[1,1],[-1,-1]]
            sage: OrientedMatroid(V4, key='vector')
            Traceback (most recent call last):
            ...
            ValueError: vector elimination failed

        """
        vectors = self.vectors()
        
        zero_found = False
        for X in vectors:
            # Axiom 1: Make sure empty is not present
            if X.is_zero():
                zero_found = True
            # Axiom 2: Make sure negative exists
            if -X not in vectors:
                raise ValueError("Every element needs an opposite")
            for Y in vectors:
                # Axiom 3: Closed under composition
                if X.composition(Y) not in vectors:
                    raise ValueError("Composition must be in vectors")
                # Axiom 4: Vector elimination
                E = X.positives().intersection(Y.negatives())

                ze1 = X.support().difference(Y.support())
                ze2 = Y.support().difference(X.support())
                ze3 = X.positives().intersection(Y.positives())
                ze4 = X.negatives().intersection(Y.negatives())
                ze = ze1.union(ze2).union(ze3).union(ze4)
                for e in E:
                    p = X.positives().union(Y.positives())
                    p.discard(e)
                    n = X.negatives().union(Y.negatives())
                    n.discard(e)
                    found = False
                    for Z in vectors:
                        if found:
                            break
                        if Z.positives().issubset(p) and Z.negatives().issubset(n) and ze.issubset(Z.support()):
                            found = True
                    if not found:
                        raise ValueError("vector elimination failed")

        if not zero_found:
            raise ValueError("Empty set is required")

        return True

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: V = [[1,1],[-1,-1],[0,0]]
            sage: M = OrientedMatroid(V, key='vector'); M
            Vector Oriented Matroid of rank 2

        """
        rep = "Vector Oriented Matroid of rank {}".format(self.rank())
        return rep

    def vectors(self):
        """
        Shorthand for :meth:`~sage.matroids.oriented_matroids.OrientedMatroids.elements`
        """
        return self.elements()
