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
from sage.categories.category import Category
from sage.categories.sets_cat import Sets


class OrientedMatroids(Category):
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


    EXAMPLES::

        sage: from oriented_matroids import OrientedMatroids
        sage: M = OrientedMatroids(); M
        Category of oriented matroids
        sage: M.super_categories()
        [Category of sets]

    .. SEEALSO::

        :class:`oriented_matroids.oriented_matroid.OrientedMatroid`

    TESTS::

        sage: TestSuite(M).run()
    """

    """
    List of all possible keys
    """
    keys = ['circuit', 'covector', 'vector', 'real_hyperplane_arrangement']

    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: from oriented_matroids import OrientedMatroids
            sage: OrientedMatroids().super_categories()
            [Category of sets]
        """
        return [Sets()]

    class ParentMethods:

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

        def to_circuit(self):
            """
            Return circuit oriented matroid.
            """
            from oriented_matroids import OrientedMatroid
            return OrientedMatroid(self.circuits(),
                                   key='circuit',
                                   groundset=self.groundset())

        def to_vector(self):
            """
            Return vector oriented matroid.
            """
            from oriented_matroids import OrientedMatroid
            return OrientedMatroid(self.vectors(),
                                   key='vector',
                                   groundset=self.groundset())

        def to_covector(self):
            """
            Return covector oriented matroid.
            """
            from oriented_matroids import OrientedMatroid
            return OrientedMatroid(self.covectors(),
                                   key='covector',
                                   groundset=self.groundset())

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
