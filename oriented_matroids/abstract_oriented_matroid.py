# -*- coding: utf-8 -*-
r"""
Category of Oriented Matroids
"""
# *****************************************************************************
#  Copyright (C) 2019 Aram Dermenjian <aram.dermenjian at gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
# ******************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.categories.sets_cat import Sets
from sage.structure.global_options import GlobalOptions


from sage.structure.element import Element
import copy

r"""
Signed Subset element
---------------------------------------

This implements a basic signed subet element which is used for oriented
matroids.

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


class SignedSubsetElement(Element):
    r"""
    Creates a signed subset.

    INPUT:

    - ``parent`` -- the parent object of the element. Usually is a class
       generated by :class:`OrientedMatroid`.
    - ``data`` -- (default: ``None``) is a tuple with information. Can be
       given in one of the following formats:
        + **as a vector** -- this is a tuple of pluses, minuses, and zeroes.
        + **as three tuples** -- the first tuple is the positives, the second
          the negatives and the third the zeroes.
        + **as a dict** -- the dictionary should have keys *positives*,
          *negatives*, and *zeroes*.

    - ``groundset`` -- (default: ``None``) if not given will construct
       the groundset from the parent, or if none is created in the parent,
       using the elements found in the data.
    - ``positives`` -- (default: ``None``) alternative to ``data``. Should be
       a tuple of elements. Requires ``negatives`` to be set.
    - ``negatives`` -- (default: ``None``) alternative to ``data``. Should be
       a tuple of elements. Requires ``positives`` to be set.
    - ``zeroes`` -- (default: ``None``) alternative to ``data``. Should be a
       tuple of elements. Requires ``positives`` and ``negatives`` to be set.

    EXAMPLES::

        sage: from oriented_matroids.oriented_matroid import OrientedMatroid
        sage: from oriented_matroids.abstract_oriented_matroid import SignedSubsetElement
        sage: M = OrientedMatroid([[1],[-1]],key='circuit');
        sage: SignedSubsetElement(M,data = (0,))
        +:
        -:
        0: 0
        sage: SignedSubsetElement(M,data = (1,))
        +: 0
        -:
        0:
        sage: M = OrientedMatroid([[1],[-1]],key='circuit', groundset=['e'])
        sage: SignedSubsetElement(M,data = (1,))
        +: e
        -:
        0:

    Elements are also lazy loaded to return the sign of elements from the
    groundset::

        sage: M = OrientedMatroid([[1],[-1]],key='circuit', groundset=['e'])
        sage: C = M.elements(); C[0]
        +: e
        -:
        0:
        sage: C[0]('e')
        1

    .. SEEALSO::

        - :class:`oriented_matroids.oriented_Matroid.OrientedMatroid`
        - :class:`oriented_matroids.oriented_matroids_category.OrientedMatroids`

    """

    def __init__(self, parent=None, data=None, groundset=None,
                 positives=None, negatives=None, zeroes=None):
        """
        Initialize ``self``.
        """
        # If our groundset isn't set but our parent has one, use its groundset
        if groundset is None:
            try:
                groundset = parent.groundset()
            except AttributeError:
                groundset = None

        # remove parent if data not present
        if parent is None \
                or (data is None and groundset is None and positives is None):
            from sage.structure.parent import Parent
            data = parent
            parent = Parent()

        # instantiate!
        self._p = set([])
        self._n = set([])
        self._z = set([])

        # If we're setting things one item at a time
        if positives is not None:
            if negatives is None:
                raise ValueError(
                    "If positives is set, negatives must be as well")

            self._p = set(positives)
            self._n = set(negatives)
            if zeroes is None:
                if groundset is None:
                    self._z = set([])
                else:
                    gs = set(groundset)
                    self._z = gs.difference(self._p).difference(self._n)
            else:
                self._z = set(zeroes)

        # If we already have a signed subset element, use it's data
        elif isinstance(data, SignedSubsetElement):
            self._p = data.positives()
            self._n = data.negatives()
            self._z = data.zeroes()

        # If we have a tuple, use its information
        elif isinstance(data, tuple):
            # if we're given vector format
            if data[0] in [-1, 0, 1, '+', '0', '-', '']:
                if groundset is not None and len(data) != len(groundset):
                    raise ValueError(
                        "Length of vector must be same number of elements as ground set")
                for i, j in enumerate(data):
                    label = i
                    if groundset is not None:
                        label = groundset[i]
                    if j == -1 or j == '-':
                        self._n.add(label)
                    elif j == 1 or j == '+':
                        self._p.add(label)
                    elif j == 0 or j == '' or j == '0':
                        self._z.add(label)
                    else:
                        raise ValueError("Must be tuple of -1, 0, 1")

            # If we have a tuple of tuples
            else:
                self._p = set(data[0])
                self._n = set(data[1])
                if len(data) > 2:
                    self._z = set(data[2])
                elif groundset is not None:
                    self._z = set(groundset).difference(
                        self._p).difference(self._n)
        # If we have a dictionary, use the keys to figure it out
        elif isinstance(data, dict):
            if 'p' in data:
                self._p = data['p']
            if 'positives' in data:
                self._p = data['positives']
            if 'n' in data:
                self._n = data['n']
            if 'negatives' in data:
                self._n = data['negatives']
            if 'z' in data:
                self._z = data['z']
            if 'zeroes' in data:
                self._z = data['zeroes']
        else:
            raise ValueError(
                "Either positives and negatives are set or data is a tuple, OrientedMatroidELement or a dict")

        # Type fix
        self._p = set(self._p)
        self._n = set(self._n)
        self._z = set(self._z)

        # Setup the ground set if it's not set yet
        if groundset is None:
            self._g = list(self._p.union(self._n).union(self._z))
        else:
            if not self.support().union(self.zeroes()).issubset(groundset):
                raise ValueError("Elements must appear in groundset")

            # Update the zeroes with everything in the ground set
            if self._z is None:
                self._z = set(groundset).difference(self.support())

            # ground set should be everything
            if not set(groundset).issubset(self.support().union(self.zeroes())):
                raise ValueError(
                    "Every element must be either positive, negative or zero")
            self._g = groundset

        self._g = list(self._g)

        Element.__init__(self, parent)

    def __call__(self, var):
        """
        Return the sign of an element in the groundset.
        """

        if var in self.positives():
            return 1
        if var in self.negatives():
            return -1
        if var in self.zeroes():
            return 0
        raise ValueError("Not in groundset")

    def __hash__(self):
        """
        Return hashed string of signed subset.
        """
        fsp = frozenset(self._p)
        fsn = frozenset(self._n)
        fsz = frozenset(self._z)
        return hash((fsp, fsn, fsz))

    def __neg__(self):
        """
        Return the opposite signed subset.
        """
        N = copy.copy(self)
        N._p = self._n
        N._n = self._p
        return N

    def __eq__(self, other):
        """
        Return whether two elements are equal.
        """
        if isinstance(other, SignedSubsetElement):
            if self._p == other._p \
                    and self._n == other._n \
                    and self._z == other._z:
                return True
        return False

    def __ne__(self, other):
        """
        Return whether two elements are not equal.
        """
        return not (self == other)

    def _cmp_(self, other):
        """
        Arbitrary comparison function so posets work.
        """
        if not isinstance(other, SignedSubsetElement):
            return 0
        return 1
        # x = len(self.support()) - len(other.support())
        # if x == 0:
        #     return x
        # return x / abs(x) * -1

    def __bool__(self):
        r"""
        Returns whether an element is not considered a zero.

        For an oriented matroid, we consider the empty set
        `\emptyset = (\emptyset,\emptyset)` to be a zero as
        it is the same as the all zero vector.
        """
        if len(self.support()) > 0:
            return True
        return False

    def __iter__(self):
        """
        Returns an iter version of self.
        """
        for e in self.groundset():
            yield self(e)

    def _repr_(self):
        """
        Return a string of the signed subset.

        EXAMPLES::

            sage: from oriented_matroids.oriented_matroid import OrientedMatroid
            sage: from oriented_matroids.abstract_oriented_matroid import SignedSubsetElement
            sage: C = [ ((1,4),(2,3)) , ((2,3),(1,4)) ]
            sage: M = OrientedMatroid(C,key='circuit')
            sage: SignedSubsetElement(M,data = ((1,4),(2,3)))
            +: 1,4
            -: 2,3
            0:

        """

        if AbstractOrientedMatroid.options.display == 'set':
            p = map(str, self.positives())
            n = map(str, self.negatives())
            z = map(str, self.zeroes())
            return "+: " + ','.join(p) + "\n" + \
                "-: " + ','.join(n) + "\n" +\
                "0: " + ','.join(z)
        if AbstractOrientedMatroid.options.display == 'vector':
            return "(" + ','.join([str(self(e)) for e in self.groundset()]) + ")"

    def _latex_(self):
        r"""
        Return a latex representation of the signed subset.

        EXAMPLES::

            sage: from oriented_matroids.oriented_matroid import OrientedMatroid
            sage: from oriented_matroids.abstract_oriented_matroid import SignedSubsetElement
            sage: C = [ ((1,4),(2,3)) , ((2,3),(1,4)) ]
            sage: M = OrientedMatroid(C,key='circuit')
            sage: latex(SignedSubsetElement(M,data = ((1,4),(2,3))))
            \left( \left{1,4\right},\left{2,3\right} \right)

        """
        if AbstractOrientedMatroid.options.display == 'set':
            p = map(str, self.positives())
            n = map(str, self.negatives())
            return "\\left( \\left{" + ','.join(p) + \
                "\\right},\\left{" + ','.join(n) + "\\right} \\right)"
        if AbstractOrientedMatroid.options.display == 'vector':
            ground_set = [str(self(e)) for e in self.groundset()]
            return "\\left(" + ','.join(ground_set) + "\\right)"

    def __copy__(self):
        """
        Return a copy of the element
        """
        return SignedSubsetElement(parent=self.parent(), groundset=self.groundset(), positives=self.positives(), negatives=self.negatives(), zeroes=self.zeroes())

    def __deepcopy__(self):
        """
        Return a copy of the element
        """
        return SignedSubsetElement(parent=self.parent(), groundset=self.groundset(), positives=self.positives(), negatives=self.negatives(), zeroes=self.zeroes())

    def to_list(self):
        """
        Convert objcet to a list
        """
        return eval("[" + ','.join([str(self(e)) for e in self.groundset()]) + "]")

    def positives(self):
        """
        Return the set of positives.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: M = OrientedMatroid([[1,-1,1],[-1,1,-1]], key='circuit')
            sage: E = M.elements()[0]
            sage: E.positives()
            {0, 2}

        """
        return self._p

    def negatives(self):
        """
        Return the set of negatives.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: M = OrientedMatroid([[1,-1,1],[-1,1,-1]], key='circuit')
            sage: E = M.elements()[0]
            sage: E.negatives()
            {1}

        """
        return self._n

    def zeroes(self):
        r"""
        Return the set of zeroes.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: M = OrientedMatroid([[1,-1,0],[-1,1,0]], key='circuit')
            sage: E = M.elements()[0]
            sage: E.zeroes()
            {2}

        """
        return self._z

    def support(self):
        r"""
        Return the support set.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: M = OrientedMatroid([[1,-1,0],[-1,1,0]], key='circuit')
            sage: E = M.elements()[0]
            sage: E.support()
            {0, 1}

        """
        return self._p.union(self._n)

    def groundset(self):
        r"""
        Return the ground set.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: M = OrientedMatroid([[1,-1,0],[-1,1,0]], key='circuit')
            sage: E = M.elements()[0]
            sage: E.groundset()
            [0, 1, 2]

        """
        return self._g

    def composition(self, other):
        r"""
        Return the composition of two elements.

        The composition of two elements `X` and `Y`,
        denoted `X \circ Y` is given componentwise
        where for `e \in E` we have `(X \circ Y)(e) = X(e)`
        if `X(e) \neq 0` else it equals `Y(e)`.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: from oriented_matroids import AbstractOrientedMatroid
            sage: AbstractOrientedMatroid.options.display='vector'
            sage: M = OrientedMatroid([[0],[1],[-1]], key='vector')
            sage: E1 = M.elements()[0]; E2 = M.elements()[1]
            sage: E1.composition(E2)
            (1)
            sage: E2.composition(E1)
            (1)
            sage: E1.composition(E2) == E2.composition(E1)
            True

        """
        p = []
        n = []
        z = []
        for e in self.groundset():
            x = self(e)
            # If x is non-zero, keep its value
            if x == 1:
                p.append(e)
            elif x == -1:
                n.append(e)
            else:
                # else grab the value of the other
                x = other(e)
                if x == 1:
                    p.append(e)
                elif x == -1:
                    n.append(e)
                else:
                    z.append(e)
        return type(self)(self.parent(), positives=p, negatives=n, zeroes=z)

    def separation_set(self, other):
        r"""
        Return the separation set between two elements.

        The separation set of two elements `X` and `Y`
        is given by `S(X,Y) = \left\{e \mid X(e) = -Y(e) \neq 0 \right\}`
        """
        return self.positives().intersection(other.negatives()).union(self.negatives().intersection(other.positives()))

    def reorientation(self, change_set):
        r"""
        Return the reorientation by a set.

        The reorientation of `X` by some `A \subseteq E` is
        the signed subset (covector) given by `{}_{-A}X` where
        `{}_{-A}X^+ = (X^+ \backslash A) \cup (X^- \cap A)` and similarly for
        `{}_{-A}X^-`.
        """
        if change_set in self.groundset():
            change_set = set([change_set])
        else:
            change_set = set(change_set)

        # ensure every elt is in the groundset
        for i in change_set:
            if i not in self.groundset():
                raise ValueError("{} is not in the ground set".format(i))

        p = self.positives().difference(change_set).union(
            self.negatives().intersection(change_set))
        n = self.negatives().difference(change_set).union(
            self.positives().intersection(change_set))
        return type(self)(self.parent(), positives=p, negatives=n, groundset=self.groundset())

    def is_conformal_with(self, other):
        r"""
        Return if the two elements are conformal.

        Two elements `X` and `Y` are *conformal* if
        `S(X,Y) = \emptyset`. This is true if and only if `X^+ \subseteq Y^+`
        and `X^- \subseteq Y^-`.
        """
        return len(self.separation_set(other)) == 0

    def is_restriction_of(self, other):
        r"""
        Return if `self` is a restriction of `other`.

        A signed subset `X` is a *restriction* of a signed subset `Y` if
        `X^+ \subsetex Y^+` and `X^- \subseteq Y^-`. If `X` is a restriction of
        `Y` we sometimes say `X` conforms to `Y`. This should not be mistaken
        with *is conformal with*.
        """
        return self.positives().issubset(other.positives()) \
            and self.negatives().issubset(other.negatives())

    def is_tope(self):
        r"""
        Return whether object is a tope.

        A covector is a tope if it is a maximal
        element in the face poset.

        .. WARNING::

            Requires the method `face_lattice` to exist in the oriented
            matroid.
        """
        if getattr(self.parent(), 'face_lattice', None) is not None:
            raise TypeError(
                "Topes are only implemented if .face_lattice() is implemented")

        return self in self.parent().topes()

    def is_simplicial(self):
        r"""
        Return whether or not a tope is simplicial.

        A tope `T` is simplicial if the interval `[0,T]` is boolean
        in the face lattice. We note that the breadth of a lattice
        can characterize this. In particular a lattice of breadth `n`
        contains a sublattice isomorphic to the Boolean lattice of `2^n`
        elements. In other words, if `[0,T]` has `2^n` elements and
        the breadth of `[0,T]` is `n` then the interval is boolean
        and thus `T` is simplicial.
        """
        if not self.is_tope():
            raise TypeError("Only topes can be simplicial")

        P = self.parent().face_lattice()
        I = P.interval(P.bottom(), self)
        PP = P.sublattice(I)
        b = PP.breadth()
        if len(I) == 2**b:
            return True
        return False

    def is_zero(self):
        """
        Return whether or not element is 0
        """
        return len([1 for e in self.groundset() if self(e) != 0]) == 0

class AbstractOrientedMatroid(UniqueRepresentation, Parent):
    r"""
    The category of oriented matroids.

    Given a set `E` a signed subset of `E` is a pair `X = (X^+,X^-)` where
    `X^+,X^- \subseteq E` and `X^+ \cap X^- = \emptyset`. The support of `X`
    is the set `\underline{X} = X^+ \cup X^-`. An *oriented matroid* is a
    pair `M = (E,\mathcal{C})` where `E` is a set and `\mathcal{C}` is a
    collection of signed subsets of `E` that satisfy certain axioms. An example
    of these axioms are the circuit axioms:

     - `\emptyset \not\in \mathcal{C}`
     - `\mathcal{C}= -\mathcal{C}`
     - for all `X,Y \in \mathcal{C}`,
       if `\underline{X} \subseteq \underline{Y}` then `X = Y` or `X = -Y`.
     - for all `X,Y \in \mathcal{C}`, `X \neq -Y`, and `e \in X^+ \cap Y^-`
       there is a `Z \in \mathcal{C}` such that
       `Z^+ \subseteq \left(X^+ \cup Y^+\right) \backslash \left\{e\right\}`
       and
       `Z^- \subseteq \left(X^- \cup Y^-\right) \backslash \left\{e\right\}`.

    See :wikipedia:`Oriented_matroid` for details.

    .. SEEALSO::

        :class:`oriented_matroids.oriented_matroid.OrientedMatroid`
    """

    """
    List of all possible keys
    """
    keys = ['circuit', 'covector', 'vector', 'real_hyperplane_arrangement']

    Element = SignedSubsetElement

    class options(GlobalOptions):
        r"""
        xxx

        @OPTIONS@

        .. NOTE::

            Changing the ``convention`` for tableaux also changes the
            ``convention`` for partitions.

        """
        NAME = 'OrientedMatroids'
        display = dict(default="set",
                       description='Changes how signed subsets are displayed.',
                       values=dict(set='display as sets',
                                   vector='display as vectors',
                                   ),
                       )

    def __init__(self, category=None):
        if category is None:
            category = Sets()
        Parent.__init__(self, category=category)

    @abstract_method
    def is_valid(self):
        r"""
        Return whether satisfies oriented matroid axioms.

        Given a set of objects, this method tests against
        a provided set of axioms for a given representation
        to ensure that we actually do have an oriented matroid.
        """
        pass

    def groundset(self):
        """
        Return the ground set of ``self``.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: A = hyperplane_arrangements.braid(2)
            sage: M = OrientedMatroid(A); M.groundset()
            (Hyperplane t0 - t1 + 0,)

        """
        return self._groundset

    def elements(self):
        """
        Return elements.

        The elements of an oriented matroid are the "defining" elements of
        the oriented matroid. For example, covectors are the elements of
        an oriented matroid defined using covectors.
        """
        return self._elements

    def circuits(self):
        """
        Return all circuits.
        """
        if "_circuits" in dir(self):
            return self._circuits
        raise NotImplementedError("Circuits not implemented")

    def cocircuits(self):
        """
        Return all cocircuits.
        """
        if "_cocircuits" in dir(self):
            return self._cocircuits
        raise NotImplementedError("Cocircuits not implemented")

    def vectors(self):
        """
        Return all vectors.
        """
        if "_vectors" in dir(self):
            return self._vectors
        raise NotImplementedError("Vectors not implemented")
        pass

    def covectors(self):
        """
        Return all covectors.
        """
        if "_covectors" in dir(self):
            return self._covectors
        raise NotImplementedError("Covectors not implemented")
        
    
    def change_type(self, new_type=None):
        '''
        Returns an oriented matroid of type specified. 
        '''
        from oriented_matroids import OrientedMatroid
        if new_type == None:
            pass
        elif new_type == 'circuit':
            return OrientedMatroid(self.circuits(),
                                   key='circuit',
                                   groundset=self.groundset())
        elif new_type == 'vector':
            return OrientedMatroid(self.vectors(),
                                   key='vector',
                                   groundset=self.groundset())
        elif new_type == 'covector':
            return OrientedMatroid(self.covectors(),
                                   key='covector',
                                   groundset=self.groundset())
        else:
            raise NotImplementedError("Type not implemented")

    def dual(self):
        """
        Return the dual oriented matroid.
        """
        pass

    @cached_method
    def matroid(self):
        r"""
        Returns the underlying matroid.
        """
        pass

    # @cached_method
    def rank(self):
        r"""
        Return the rank.

        The *rank* of an oriented matroid is the rank of its underlying
        matroid.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: A = hyperplane_arrangements.braid(3)
            sage: M = OrientedMatroid(A); M.rank()
            2
            sage: A = hyperplane_arrangements.braid(4)
            sage: M = OrientedMatroid(A); M.rank()
            3
        """
        return self.matroid().rank()

    def an_element(self):
        """
        Returns an arbitrary element.
        """
        from sage.misc.prandom import randint
        els = self.elements()
        i = randint(1, len(els))
        return els[i-1]

    def face_poset(self, facade=False):
        r"""
        Returns the (big) face poset.

        The *(big) face poset* is the poset on covectors such that `X \leq Y`
        if and only if `S(X,Y) = \emptyset` and
        `\underline{Y} \subseteq \underline{X}`.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: C = [ [1,1,1], [1,1,0],[1,1,-1],[1,0,-1],[1,-1,-1],[0,-1,-1],
            ....: [-1,-1,-1],[0,1,1],[-1,1,1],[-1,0,1],[-1,-1,1],[-1,-1,0],
            ....: [0,0,0]]
            sage: M = OrientedMatroid(C, key='covector')
            sage: M.face_poset()
            Finite meet-semilattice containing 13 elements
        """
        from sage.combinat.posets.lattices import MeetSemilattice
        els = self.covectors()
        rels = [
            (Y, X)
            for X in els
            for Y in els
            if Y.is_conformal_with(X) and Y.support().issubset(X.support())
        ]
        return MeetSemilattice((els, rels), cover_relations=False, facade=facade)

    def face_lattice(self, facade=False):
        r"""
        Returns the (big) face lattice.

        The *(big) face lattice* is the (big) face poset with a top element
        added.

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid
            sage: C = [ [1,1,1], [1,1,0],[1,1,-1],[1,0,-1],[1,-1,-1],[0,-1,-1],
            ....: [-1,-1,-1],[0,1,1],[-1,1,1],[-1,0,1],[-1,-1,1],[-1,-1,0],
            ....: [0,0,0]]
            sage: M = OrientedMatroid(C, key='covector')
            sage: M.face_lattice()
            Finite lattice containing 14 elements
        """
        from sage.combinat.posets.lattices import LatticePoset
        els = self.covectors()
        rels = [
            (Y, X)
            for X in els
            for Y in els
            if Y.is_conformal_with(X) and Y.support().issubset(X.support())
        ]

        # Add top element
        for i in els:
            rels.append((i, 1))
        els.append(1)
        return LatticePoset((els, rels), cover_relations=False, facade=facade)

#             P = self.face_poset()
#             rels = P.relations()
#             els = [1]
#             for i in P:
#                 els.append(i.element)
#                 rels.append([i.element, 1])
#
#             return LatticePoset((els,rels),
#                                 cover_relations=False,
#                                 facade=facade)

    def topes(self):
        r"""
        Returns the topes.

        A *tope* is the maximal covector in the face poset.
        """
        return self.face_poset(facade=True).maximal_elements()

    def tope_poset(self, base_tope, facade=False):
        r"""
        Returns the tope poset.

        The tope poset is the poset `(\mathcal{T}, B)` where `\mathcal{T}`
        is the set of topes and `B` is a distinguished tope called the
        *base tope*. The order is given by inclusion of separation sets
        from the base tope: `X \leq Y` if and only if
        `S(B, X) \subseteq S(B, Y)`.
        """
        from sage.combinat.posets.posets import Poset
        els = self.topes()
        rels = [
            (X, Y)
            for X in els
            for Y in els
            if base_tope.separation_set(X).issubset(base_tope.separation_set(Y))
        ]

        return Poset((els, rels), cover_relations=False, facade=facade)

    def is_simplicial(self):
        r"""
        Returns if the oriented matroid is simplicial.

        An oriented matroid is *simplicial* if every tope is simplicial.

        .. SEEALSO::

            :meth:`~sage.matroids.oriented_matroids.signed_subset_element.SignedSubsetElement.is_simplicial`
        """
        for t in self.topes():
            if not t.is_simplicial():
                return False
        return True

    def is_acyclic(self):
        r"""
        Return if oriented matroid is acyclic.

        A covector oriented matroid is *acyclic* if there exists a positive
        tope where a *positive tope* is defined as a tope with no
        negative part.
        """
        for t in self.topes():
            if len(t.negatives()) == 0:
                return True
        return False

    def deletion(self, change_set):
        r"""
        Returns a covector oriented matroid of a deletion.

        Let `M = (E, \mathcal{L})` be an oriented matroid over a set `E`
        and a set of covectors `\mathcal{L}`. Given `A \subseteq E`, the
        *deletion* is the (covector) oriented matroid
        `M\backslash A = (E \backslash A, \mathcal{L} \backslash A)` where

        .. MATH::

            \mathcal{C} \backslash A = \left\{ X\mid_{E \backslash A} : X \in \mathcal{C}\right\}

        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroid

        """
        if change_set in self.groundset():
            change_set = set([change_set])
        else:
            change_set = set(change_set)

        from oriented_matroids.oriented_matroid import deep_tupler
        groundset = set(self.groundset()).difference(change_set)
        groundset = deep_tupler(groundset)
        data = []
        for c in self.covectors():
            p = tuple(c.positives().difference(change_set))
            n = tuple(c.negatives().difference(change_set))
            z = tuple(c.zeroes().difference(change_set))
            data.append((p, n, z))
        data = deep_tupler(data)

        from oriented_matroids import OrientedMatroid
        return OrientedMatroid(data, key='covector', groundset=groundset)

    def restriction(self, change_set):
        r"""
        Returns a covector oriented matroid of a restriction.

        Given an oriented matroid `M = (E, \mathcal{L})` where `E` is a
        set and `\mathcal{L}` is the set of covectors. Given
        `A \subseteq E`, the *restriction* is the (covector) oriented
        matroid `M / A = (E \backslash A, \mathcal{C} / A)` where

        .. MATH::

            \mathcal{C} / A = \left\{ X\mid_{E \backslash A} : X \in \mathcal{C} \text{ and} A \subseteq X^0 \right\}

        """
        # sage: from oriented_matroids import OrientedMatroid
        # sage: A = hyperplane_arrangements.braid(3)
        # sage: M = OrientedMatroid(A); M
        # Covector Oriented Matroid of rank 3
        # sage: R = M.restriction(M.groundset()[1]); R
        # Covector Oriented Matroid of rank 2
        # sage: R.elements()
        # [(0,0), (1,1), (-1,-1)]
        if change_set in self.groundset():
            change_set = set([change_set])
        else:
            change_set = set(change_set)

        from oriented_matroids.oriented_matroid import deep_tupler
        groundset = set(self.groundset()).difference(change_set)
        groundset = deep_tupler(groundset)
        data = []
        for c in self.covectors():
            p = tuple(c.positives().difference(change_set))
            n = tuple(c.negatives().difference(change_set))
            z = tuple(c.zeroes().difference(change_set))
            if change_set.issubset(c.zeroes()):
                data.append((p, n, z))
        data = deep_tupler(data)

        from oriented_matroids import OrientedMatroid
        return OrientedMatroid(data, key='covector', groundset=groundset)

    def loops(self):
        r"""
        Returns the loops of an oriented matroid.

        A *loop* is an element `e \in E` such that there is a
        tope `T \in \mathcal{T}` with `T(e) = 0`. In particular
        if `T(e) = 0` for some `T`, then it is true for all
        `T \in \mathcal{T}`.
        """
        T = self.topes()[0]
        loops = []
        gs = self.groundset()
        for i, j in enumerate(T):
            if T(j) == 0:
                loops.append(gs[i])
        return loops

    def are_parallel(self, e, f):
        r"""
        Returns whether two elements in ground set are parallel.

        Two elements in the ground set `e, f \in E` are parallel if they
        are not loops and for all `X \in \mathcal{C}`, `X(e) = 0`
        implies `X(f) = 0`. See Lemma 4.1.10 [BLSWZ1999]_ .
        """
        gs = set(self.groundset()).difference(set(self.loops()))
        if e not in gs or f not in gs:
            raise ValueError(
                "Elements must be in groundset and must not be loops")
        for i in self.elements():
            if i(e) == 0 and i(f) != 0:
                return False
        return True

    def is_simple(self):
        r"""
        Returns if the oriented matroid is simple.

        An oriented matroid is *simple* if there are no loops
        and no parallel elements.
        """
        from sage.combinat.subset import Subsets
        if len(self.loops()) > 0:
            return False
        for i in Subsets(self.groundset(), 2):
            if self.are_parallel(i[0], i[1]):
                return False
        return True

    def _element_constructor_(self, x):
        r"""
        Determine if ``x`` may be viewed as belonging to ``self``.
        """
        try:
            if x in self.elements():
                return x
            return False
        except ValueError:
            return False