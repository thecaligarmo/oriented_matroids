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

from sage.structure.parent import Parent
from oriented_matroids.covector_oriented_matroid import CovectorOrientedMatroid


class RealHyperplaneArrangementOrientedMatroid(CovectorOrientedMatroid):
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

    @staticmethod
    def __classcall__(cls, data, groundset=None):
        """
        Normalize arguments and set class.
        """
        
        return super(RealHyperplaneArrangementOrientedMatroid, cls) \
            .__classcall__(cls,
                           data=data,
                           groundset=groundset)

    def __init__(self, data, groundset=None):
        """
        Initialize ``self``
        """
        Parent.__init__(self)

        self._arrangement = data

        if data and groundset is None:
            groundset = tuple(data.hyperplanes())

        if groundset is None:
            self._groundset = groundset
        else:
            self._groundset = tuple(groundset)

        # Set up our covectors after our groundset is made
        faces = [i[0] for i in self._arrangement.closed_faces()]
        self._covectors = [self.element_class(
            self, data=f, groundset=self._groundset) for f in faces]
        self._elements = self._covectors

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        try:
            rep = "Hyperplane arrangement oriented matroid of rank {}".format(
                self.arrangement().rank())
        except ValueError:
            rep = "Hyperplane arrangement oriented matroid"
        return rep

    def is_valid(self):
        """
        Return whether or not the arrangement is an oriented matroid
        """

        if not self.arrangement().is_central():
            raise ValueError(
                "Hyperplane arrangements must be central to be an oriented matroid.")

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
