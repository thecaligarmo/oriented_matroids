r"""
Oriented matroid with circuit axioms
-------------------------------------

This implements an oriented matroid using the circuit axioms.

AUTHORS:

- Aram Dermenjian (...): Initial version
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
from sage.categories.oriented_matroids import OrientedMatroids

from sage.matroids.oriented_matroids.signed_subset_element import SignedSubsetElement

class CircuitOrientedMatroid(UniqueRepresentation,Parent):
    r"""
    An oriented matroid implemented using circuit axioms.

    This implements an oriented matroid using the circuit axioms. For this
    let `\mathcal{C}` be a set of signed subsets and `E` a ground set. Then
    a pair `M = (E,\mathcal{C})` is an oriented matroid using the circuit
    axioms if (see Definition 3.2.1 in [BLSWZ1999]_):

        - `\emptyset \notin \mathcal{C}`
        - `\mathcal{C} = -\mathcal{C}`
        - For all `X,Y \in \mathcal{C}`, if the support of `X` is contained in the support of `Y` then `X = Y` or `X = -Y`
        - For all `X,Y \in \mathcal{C}`, `X \neq -Y`, and `e \in X^+ \cap Y^-` there exists a `Z \in \mathcal{C}` such that `Z^+ \subseteq (X^+ \cup Y^+) \backslash \left\{e\right\}` and `Z^- \subseteq (X^- \cup Y^-) \backslash \left\{e\right\}`.

    INPUT:

    - ``data`` -- a tuple containing SignedSubsetElement elements or data
      that can be used to construct :class:`SignedSubsetElement` elements
    - ``goundset`` -- (default: ``None``) is the groundset for the
      data. If not provided, we grab the data from the signed subsets.

    EXAMPLES::
        sage:
        sage: M = OrientedMatroid([[1],[-1]],key='circuit'); M
        Circuit Oriented Matroid of rank 1
        sage: M.groundset()
        [0]
        
        sage: C = [ ((1,4),(2,3)) , ((2,3),(1,4)) ]
        sage: M = OrientedMatroid(C,key='circuit'); M
        Circuit Oriented Matroid of rank 4
        sage: M.groundset()
        [1, 2, 3, 4]

    .. SEEALSO::

        :class:`OrientedMatroid`
        :class:`OrientedMatroids`
    """
    Element = SignedSubsetElement

    @staticmethod
    def __classcall__(cls, data, groundset = None):
        """
        Normalize arguments and set class.
        """
        category = OrientedMatroids()
        return super(CircuitOrientedMatroid, cls).__classcall__(cls, data, groundset = groundset, category=category)

    def __init__(self,data, groundset=None,category=None):
        """
        Initialize ``self``.
        """
        Parent.__init__(self,category = category)

        # Set up our circuits
        circuits = []
        for d in data:
            # Convert to the appropriate element class
            circuits.append(self.element_class(self,data=d, groundset=groundset))

        # If our groundset is none, make sure the groundsets are the same for all elements
        if groundset is None:
            groundset = circuits[0].groundset()
            for X in circuits:
                if X.groundset() != groundset:
                    raise ValueError("Groundsets must be the same")

        self._circuits = circuits
        self._groundset = list(groundset)


    def is_valid(self):
        """
        Return whether our circuits satisfy the circuit axioms.
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
                        raise ValueError("Only same/opposites can have same support")
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
        """
        rep = "Circuit Oriented Matroid of rank {}".format(self.rank())
        return rep
    
    def groundset(self):
        """
        Return a list of groundset.
        """
        return self._groundset

    def elements(self):
        """
        Return set of elements.
        """
        return self.circuits()

    def circuits(self):
        """
        Shorthand for :meth:`~sage.categories.oriented_matroids.OrientedMatroids.elements`.
        """
        return self._circuits
