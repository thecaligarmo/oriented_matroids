r"""
Oriented matroid from real hyperplane arrangements
--------------------------------------------------

This implements an oriented matroid from real hyperplane arrangements

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

class RealHyperplaneArrangementOrientedMatroid(UniqueRepresentation, Parent):
    r"""
    An oriented matroid implemented from a real hyperplane arrangement.

    This implements an oriented matroid using hyperplane arrangements.
    Oriented matroids arise from central hyperplane arrangements.

    INPUT:

    - ``data`` -- a :class:`HyperplaneArrangementElement` element.
    - ``goundset`` -- (default: ``None``) is the groundset for the
      data. If not provided, we grab the data from the hyperplane
      arrangement

    EXAMPLES::

        sage: from oriented_matroids import OrientedMatroid
        sage: A = hyperplane_arrangements.braid(3)
        sage: M = OrientedMatroid(A); M
        Hyperplane arrangement oriented matroid of rank 2
        sage: A = hyperplane_arrangements.braid(5)
        sage: M = OrientedMatroid(A); M
        Hyperplane arrangement oriented matroid of rank 4
        sage: A = hyperplane_arrangements.Catalan(3)
        sage: M = OrientedMatroid(A); M
        Traceback (most recent call last):
        ...
        ValueError: Hyperplane arrangements must be central to be an oriented matroid.
        sage: G = Graph({1:[2,4],2:[3,4]})
        sage: A = hyperplane_arrangements.graphical(G)
        sage: M = OrientedMatroid(A); M
        Hyperplane arrangement oriented matroid of rank 3


    .. SEEALSO::

        :class:`oriented_matroids.oriented_matroid.OrientedMatroid`
        :class:`oriented_matroids.oriented_matroids_category.OrientedMatroids`
    """
    Element = SignedVectorElement
    key='real_hyperplane_arrangement'

    @staticmethod
    def __classcall__(cls, data, groundset = None):
        """
        Normalize arguments and set class.
        """
        category = OrientedMatroids()
        return super(RealHyperplaneArrangementOrientedMatroid, cls).__classcall__(cls, data=data, groundset = groundset, category=category)

    def __init__(self,data, groundset=None, category=None):
        """
        Initialize ``self``
        """
        Parent.__init__(self,category = category)

        
        self._arrangement = data
        if data and groundset is None:
            groundset = tuple(data.hyperplanes())

        if groundset is None:
            self._groundset = groundset
        else:
            self._groundset = tuple(groundset)


    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        try:
            rep = "Hyperplane arrangement oriented matroid of rank {}".format(self.arrangement().rank())
        except:
            rep = "Hyperplane arrangement oriented matroid"
        return rep

    def is_valid(self):
        """
        Return whether or not the arrangement is an oriented matroid
        """

        if not self.arrangement().is_central():
            raise ValueError("Hyperplane arrangements must be central to be an oriented matroid.")

        return True

    def arrangement(self):
        """
        Return the arrangement.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: G = Graph({1:[2,4],2:[3,4]})
            sage: A = hyperplane_arrangements.graphical(G)
            sage: M = OrientedMatroid(A); M
            Hyperplane arrangement oriented matroid of rank 3
            sage: M.arrangement()
            Arrangement <t1 - t2 | t1 - t3 | t0 - t1 | t0 - t3>

        """
        return self._arrangement

    def elements(self):
        """
        Return the elements.
        """

        faces = [i[0] for i in self.arrangement().closed_faces()]
        self._elements = [self.element_class(self,data=f,groundset=self.groundset()) for f in faces]
        return self._elements

    def matroid(self):
        """
        Return the underlying matroid.
        """
        from sage.matroids.constructor import Matroid
        from sage.matrix.constructor import matrix
        m = matrix([H.normal() for H in self.arrangement().hyperplanes()])
        return Matroid(matrix=m, groundset=self.groundset())

    def deletion(self, hyperplanes):
        """
        Return the hyperplane arrangement oriented matroid with hyperplanes removed

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: G = Graph({1:[2,4],2:[3,4,5],3:[4,6,8],4:[7],5:[8]})
            sage: A = hyperplane_arrangements.graphical(G)
            sage: H = [A.hyperplanes()[i] for i in range(2,5)]
            sage: M = OrientedMatroid(A)
            sage: M = OrientedMatroid(A); M
            Hyperplane arrangement oriented matroid of rank 7
            sage: M2 = M.deletion(H); M2
            Hyperplane arrangement oriented matroid of rank 6

        """
        A = self.arrangement()
        if isinstance(hyperplanes, list) or isinstance(hyperplanes, tuple):
            for h in hyperplanes:
                A = A.deletion(h)
        else:
            A = A.deletion(h)
        return RealHyperplaneArrangementOrientedMatroid(A)

    def face_poset(self, facade=False):
        r"""
        Returns the (big) face poset.

        The *(big) face poset* is the poset on covectors such that `X \leq Y`
        if and onlyif `S(X,Y) = \emptyset` and `\underline{Y} \subseteq \underline{X}`.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: G = Graph({1:[2,4],2:[3,4]})
            sage: A = hyperplane_arrangements.graphical(G)
            sage: M = OrientedMatroid(A); M
            Hyperplane arrangement oriented matroid of rank 3
            sage: M.face_poset()
            Finite poset containing 39 elements


        """
        from sage.combinat.posets.posets import Poset
        els = self.arrangement().closed_faces(labelled=False)
        rels = lambda x,y: y.contains(x.representative_point())
        return Poset((els, rels), cover_relations=False, facade=facade)

    def face_lattice(self, facade=False):
        r"""
        Returns the (big) face lattice.

        The *(big) face lattice* is the (big) face poset with a top element added.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: G = Graph({1:[2,4],2:[3,4]})
            sage: A = hyperplane_arrangements.graphical(G)
            sage: M = OrientedMatroid(A); M
            Hyperplane arrangement oriented matroid of rank 3
            sage: M.face_lattice()
            Finite lattice containing 40 elements

        """
        from sage.combinat.posets.lattices import LatticePoset
        els = self.arrangement().closed_faces(labelled=False) + (1,)
        rels = lambda x,y: True if (y == 1) else False if (x == 1) else y.contains(x.representative_point())
        return LatticePoset((els, rels), cover_relations=False, facade=facade)

