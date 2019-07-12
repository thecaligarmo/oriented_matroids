# -*- coding: utf-8 -*-
r"""
Category of Oriented Matroids
"""
#*****************************************************************************
#  Copyright (C) 2019 Aram Dermenjian <aram.dermenjian at gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

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
    pair `M = (E,\mathcal{C})` where `E` is a set and `\mathcal{C}` is a collection
    of signed subsets of `E` that satisfy certain axioms. An example of
    these axioms are the circuit axioms:

     - `\emptyset \not\in \mathcal{C}`
     - `\mathcal{C}= -\mathcal{C}`
     - for all `X,Y \in \mathcal{C}`, if `\underline{X} \subseteq \underline{Y}`
       then `X = Y` or `X = -Y`.
     - for all `X,Y \in \mathcal{C}`, `X \neq -Y`, and `e \in X^+ \cap Y^-` there
       is a `Z \in \mathcal{C}` such that
       `Z^+ \subseteq \left(X^+ \cup Y^+\right) \backslash \left\{e\right\}` and
       `Z^- \subseteq \left(X^- \cup Y^-\right) \backslash \left\{e\right\}`.
    
    See :Wikipedia:`Oriented_matroid` for details.


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
                sage: M = OrientedMatroid(A, key='covector'); M.groundset()
                (Hyperplane t0 - t1 + 0,)

            """
            return self._groundset

        def elements(self):
            """
            Return all elements.

            EXAMPLES::

                sage: from oriented_matroids import OrientedMatroid
                sage: A = hyperplane_arrangements.braid(2)
                sage: M = OrientedMatroid(A, key='covector'); M.elements()
                [(0), (1), (-1)]

            """
            return self._elements

        @cached_method
        def matroid(self):
            r"""
            Returns the underlying matroid.

            Given an oriented matroid, the *underlying matroid* is the matroid
            whose ground set is the ground set of the oriented matroid
            and the elements are the set of supports of all the signed
            subsets.

            EXAMPLES::

                sage: from oriented_matroids import OrientedMatroid
                sage: A = hyperplane_arrangements.braid(3)
                sage: M = OrientedMatroid(A, key='covector'); M.matroid()
                Matroid of rank 3 on 3 elements with 1 bases

            """
            from sage.matroids.constructor import Matroid
            data = list(set([frozenset(X.support()) for X in self.elements()]))
            return Matroid(groundset = self.groundset(), data = data)


        @cached_method
        def rank(self):
            r"""
            Return the rank.

            The *rank* of an oriented matroid is the rank of its underlying matroid.

            EXAMPLES::

                sage: from oriented_matroids import OrientedMatroid
                sage: A = hyperplane_arrangements.braid(3)
                sage: M = OrientedMatroid(A, key='covector'); M.rank()
                3
                sage: A = hyperplane_arrangements.braid(4)
                sage: M = OrientedMatroid(A, key='covector'); M.rank()
                6
            """
            return self.matroid().rank()

        def an_element(self):
            """
            Returns an arbitrary element.
            """
            from sage.misc.prandom import randint
            els = self.elements()
            i = randint(1,len(els))
            return els[i-1]


        def face_poset(self, facade=False):
            r"""
            Returns the (big) face poset.
            """
            pass

        def face_lattice(self, facade=False):
            r"""
            Returns the (big) face lattice.
            """
            pass


        def topes(self):
            r"""
            Returns the topes.
    
            A *tope* is the maximal elements in the face poset.
            """
            return self.face_poset(facade=True).maximal_elements()
    
        def tope_poset(self, base_tope, facade=False):
            r"""
            Returns the tope poset.
    
            The tope poset is the poset `(\mathcal{T}, B)` where `\mathcal{T}`
            is the set of topes and `B` is a distinguished tope called the 
            *base tope*. The order is given by inclusion of separation sets from
            the base tope: `X \leq Y` if and only if `S(B, X) \subseteq S(B, Y)`.
            """
            from sage.combinat.posets.posets import Poset
            els = self.topes()
            rels = [ (X,Y) for X in els for Y in els if base_tope.separation_set(X).issubset(base_tope.separation_set(Y))]
            return Poset((els,rels), cover_relations = False, facade=facade)
    
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
            Returns an oriented matroid of a deletion.
    
            A *deletion* of an oriented matroid `M = (E, \mathcal{C})` is
            the oriented matroid `M\backslash A = (E \backslash A, \mathcal{C} \backslash A)` where
            
            .. MATH::
    
                \mathcal{C} \backslash A = \left\{ X\mid_{E \backslash A} : X \in \mathcal{C}\right\}

            EXAMPLES::

                sage: from oriented_matroids import OrientedMatroid
                sage: C = [ ((1,4),(2,3)) , ((2,3),(1,4)) ]
                sage: M = OrientedMatroid(C,key='circuit'); M
                Circuit oriented matroid of rank 4
                sage: D = M.deletion(1)
                sage: D.elements()
                [+: 4
                 -: 2,3
                 0: , +: 2,3
                 -: 4
                 0: ]

            """
            if change_set in self.groundset():
                change_set = set([change_set])
            else:
                change_set = set(change_set)
    
            from oriented_matroids.oriented_matroid import deep_tupler
            groundset = deep_tupler(set(self.groundset()).difference(change_set))
            data = []
            for c in self.elements():
                p = tuple(c.positives().difference(change_set))
                n = tuple(c.negatives().difference(change_set))
                z = tuple(c.zeroes().difference(change_set))
                data.append( (p,n,z) )
            data = deep_tupler(data)
            return type(self)(data, groundset=groundset)
    
        def restriction(self, change_set):
            r"""
            Returns an oriented matroid of a restriction.
    
            A *restriction* of an oriented matroid `M = (E, \mathcal{C})` is
            the oriented matroid `M / A = (E \backslash A, \mathcal{C} / A)` where

            .. MATH::

                \mathcal{C} / A = \left\{ X\mid_{E \backslash A} : X \in \mathcal{C} \text{ and} A \subseteq X^0 \right\}

            EXAMPLES::


            """
                #sage: from oriented_matroids import OrientedMatroid
                #sage: A = hyperplane_arrangements.braid(3)
                #sage: M = OrientedMatroid(A, key='covector'); M
                #Covector Oriented Matroid of rank 3
                #sage: R = M.restriction(M.groundset()[1]); R
                #Covector Oriented Matroid of rank 2
                #sage: R.elements()
                #[(0,0), (1,1), (-1,-1)]
            if change_set in self.groundset():
                change_set = set([change_set])
            else:
                change_set = set(change_set)
    
            from oriented_matroids.oriented_matroid import deep_tupler
            groundset = deep_tupler(set(self.groundset()).difference(change_set))
            data = []
            for c in self.elements():
                p = tuple(c.positives().difference(change_set))
                n = tuple(c.negatives().difference(change_set))
                z = tuple(c.zeroes().difference(change_set))
                if change_set.issubset(c.zeroes()):
                    data.append( (p,n,z) )
            data = deep_tupler(data)
            return type(self)(data, groundset=groundset)
    
        def loops(self):
            r"""
            Returns the loops of an oriented matroid.
    
            A *loop* is an element `e \in E` such that there is a
            tope `T \in \mathcal{T}` with `T(e) = 0`. In particular
            if `T(e) = 0` for some `T`, then it is true for all `T \in \mathcal{T}`.
            """
            T = self.topes()[0]
            loops = []
            gs = self.groundset()
            for i,j in enumerate(T):
                if T(j) == 0:
                    loops.append(gs[i])
            return loops
    
        def are_parallel(self, e, f):
            r"""
            Returns whether two elements in ground set are parallel.
    
            Two elements in the ground set `e, f \in E` are parallel if they
            are not loops and for all `X \in \mathcal{C}`, `X(e) = 0` implies `X(f) = 0`.
            See Lemma 4.1.10 [BLSWZ1999]_ .
            """
            gs = set(self.groundset()).difference(set(self.loops()))
            if e not in gs or f not in gs:
                raise ValueError("Elements must be in groundset and must not be loops")
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
            except:
                return False
    
