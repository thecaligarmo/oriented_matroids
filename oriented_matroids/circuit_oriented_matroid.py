r"""
Oriented matroid with circuit axioms
-------------------------------------

This implements an oriented matroid using the circuit axioms.

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
from oriented_matroids.signed_subset_element import SignedSubsetElement


class CircuitOrientedMatroid(UniqueRepresentation, Parent):
    r"""
    An oriented matroid implemented using circuit axioms.

    This implements an oriented matroid using the circuit axioms. For this
    let `\mathcal{C}` be a set of signed subsets and `E` a ground set. Then
    a pair `M = (E,\mathcal{C})` is an oriented matroid using the circuit
    axioms if (see Definition 3.2.1 in [BLSWZ1999]_):

        - `\emptyset \notin \mathcal{C}`
        - `\mathcal{C} = -\mathcal{C}`
        - For all `X,Y \in \mathcal{C}`, if the support of `X` is contained
          in the support of `Y` then `X = Y` or `X = -Y`
        - For all `X,Y \in \mathcal{C}`, `X \neq -Y`, and
          `e \in X^+ \cap Y^-` there exists a `Z \in \mathcal{C}` such that
          `Z^+ \subseteq (X^+ \cup Y^+) \backslash \left\{e\right\}` and
          `Z^- \subseteq (X^- \cup Y^-) \backslash \left\{e\right\}`.

    INPUT:

    - ``data`` -- a tuple containing SignedSubsetElement elements or data
      that can be used to construct :class:`SignedSubsetElement` elements
    - ``goundset`` -- (default: ``None``) is the groundset for the
      data. If not provided, we grab the data from the signed subsets.

    EXAMPLES::

        sage: from oriented_matroids import OrientedMatroid
        sage: M = OrientedMatroid([[1],[-1]],key='circuit'); M
        Circuit oriented matroid of rank 1
        sage: M.groundset()
        (0,)

        sage: C = [ ((1,4),(2,3)) , ((2,3),(1,4)) ]
        sage: M = OrientedMatroid(C,key='circuit'); M
        Circuit oriented matroid of rank 4
        sage: M.groundset()
        (1, 2, 3, 4)

    .. SEEALSO::

        :class:`oriented_matroids.oriented_matroid.OrientedMatroid`
        :class:`oriented_matroids.oriented_matroids_category.OrientedMatroids`
    """
    Element = SignedSubsetElement

    @staticmethod
    def __classcall__(cls, data, groundset=None):
        """
        Normalize arguments and set class.
        """

        category = OrientedMatroids()
        return super(CircuitOrientedMatroid, cls) \
            .__classcall__(cls,
                           data=data,
                           groundset=groundset,
                           category=category)

    def __init__(self, data, groundset=None, category=None):
        """
        Initialize ``self``.
        """
        Parent.__init__(self, category=category)

        # Set up our circuits
        circuits = []
        if data:
            for d in data:
                # Convert to the appropriate element class
                circuits.append(self.element_class(self,
                                                   data=d,
                                                   groundset=groundset))

        # If our groundset is none, make sure the groundsets are the same for
        # all elements
        if groundset is None and len(circuits) > 0:
            groundset = circuits[0].groundset()
            for X in circuits:
                if X.groundset() != groundset:
                    raise ValueError("Groundsets must be the same")

        self._elements = circuits
        if groundset is None:
            self._groundset = None
        else:
            self._groundset = tuple(groundset)

    def is_valid(self):
        """
        Return whether our circuits satisfy the circuit axioms.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: C = [ ((1,4),(2,3)) , ((2,3),(1,4)) ]
            sage: M = OrientedMatroid(C,key='circuit')
            sage: M.is_valid()
            True
            sage: C2 = [ ((1,4),(2,3)) , ((1,3),(2,4)) , ((2,3),(1,4)) ]
            sage: OrientedMatroid(C2,key='circuit')
            Traceback (most recent call last):
            ...
            ValueError: Only same/opposites can have same support

            sage: C3 = [ ((),()) , ((1,4),(2,3)) , ((2,3),(1,4)) ]
            sage: OrientedMatroid(C3,key='circuit',groundset=[1,2,3,4])
            Traceback (most recent call last):
            ...
            ValueError: Empty set not allowed

            sage: C4= [ ((1,),()) , ((1,4),(2,3)) , ((2,3),(1,4)) ]
            sage: OrientedMatroid(C4,key='circuit',groundset=[1,2,3,4])
            Traceback (most recent call last):
            ...
            ValueError: Every element needs an opposite

        """
        circuits = self.circuits()

        for X in circuits:
            # Axiom 1: Make sure empty is not present
            if X.is_zero():
                raise ValueError("Empty set not allowed")
            # Axiom 2: Make sure negative exists
            if -X not in circuits:
                raise ValueError("Every element needs an opposite")
            for Y in circuits:
                # Axiom 3: supports must not be contained
                if X.support().issubset(Y.support()):
                    if X != Y and X != -Y:
                        raise ValueError(
                            "Only same/opposites can have same support")
                # Axiom 4: Weak elimination
                if X != -Y:
                    E = X.positives().intersection(Y.negatives())
                    for e in E:
                        p = X.positives().union(Y.positives())
                        p.discard(e)
                        n = X.negatives().union(Y.negatives())
                        n.discard(e)
                        found = False
                        for Z in circuits:
                            if found:
                                break
                            if Z.positives().issubset(p) and Z.negatives().issubset(n):
                                found = True
                        if not found:
                            raise ValueError("Weak elimination failed")

        return True

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: C = [ ((1,),(2,)) , ((2,),(1,)) , ((3,),(4,)) , ((4,),(3,))]
            sage: OrientedMatroid(C,key='circuit',groundset=[1,2,3,4])
            Circuit oriented matroid of rank 2

        """
        try:
            rep = "Circuit oriented matroid of rank {}".format(self.rank())
        except ValueError:
            rep = "Circuit oriented matroid"
        return rep

    def circuits(self):
        """
        Shorthand for :meth:`~oriented_matroids.oriented_matroids_category.OrientedMatroids.elements`.
        """
        return self.elements()
