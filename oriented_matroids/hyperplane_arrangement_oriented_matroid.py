r"""
Oriented matroid from hyperplane arrangements
---------------------------------------

This implements an oriented matroid from hyperplane arrangements

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

class HyperplaneArrangementOrientedMatroid(UniqueRepresentation, Parent):
    r"""
    An oriented matroid implemented from a hyperplane arrangement.

    This implements an oriented matroid using hyperplane arrangements.
    Oriented matroids arise from central hyperplane arrangements.

    INPUT:

    - ``data`` -- a :class:`HyperplaneArrangementElement` element.
    - ``goundset`` -- (default: ``None``) is the groundset for the
      data. If not provided, we grab the data from the hyperplane
      arrangement

    EXAMPLES::

        sage: from oriented_matroids import OrientedMatroid

    .. SEEALSO::

        :class:`oriented_matroids.oriented_matroid.OrientedMatroid`
        :class:`oriented_matroids.oriented_matroids_category.OrientedMatroids`
    """
    Element = SignedVectorElement

    @staticmethod
    def __classcall__(cls, data, groundset = None):
        """
        Normalize arguments and set class.
        """
        category = OrientedMatroids()
        return super(HyperplaneArrangementOrientedMatroid, cls).__classcall__(cls, data=data, groundset = groundset, category=category)

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

        EXAMPLES::

        """

        if not self.arrangement().is_central():
            raise ValueError("Hyperplane arrangements must be central to be an oriented matroid.")

        return True

    def arrangement(self):
        """
        Return the arrangement.
        """
        return self._arrangement

    def elements(self):
        """
        Return the elements.
        """

        faces = [i[0] for i in self.arrangement().closed_faces()]
        self._elements = [self.element_class(self,data=f,groundset=self.groundset()) for f in faces]
        return self._elements

    def deletion(self, hyperplanes):
        """
        Return the hyperplane arrangement oriented matroid with hyperplanes removed
        """
        
        # self.arrangement().deletion(H); "H a hyperplane
        return self.parent().deletion(hyperplanes)


    def face_poset(self, facade=False):
        r"""
        Returns the (big) face poset.

        The *(big) face poset* is the poset on covectors such that `X \leq Y`
        if and onlyif `S(X,Y) = \emptyset` and `\underline{Y} \subseteq \underline{X}`.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid

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

        """
        from sage.combinat.posets.lattices import LatticePoset
        els = self.arrangement().closed_faces(labelled=False) + (1,)
        rels = lambda x,y: True if (y == 1) else False if (x == 1) else y.contains(x.representative_point())
        return LatticePoset((els, rels), cover_relations=False, facade=facade)

