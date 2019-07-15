r"""
Oriented matroid mapper

Allows you to go from one oriented matroid type to another.

AUTHORS:

- Aram Dermenjian (2019-07-12): initial version

"""

#*****************************************************************************
#       Copyright (C) 2019 Aram Dermenjian <aram.dermenjian at gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from oriented_matroids.oriented_matroids_category import OrientedMatroids
from oriented_matroids import OrientedMatroid

class OrientedMatroidMapper:

    def __init__(self,fromOM,toType, groundset=None):
        r"""
        Initialize our two desired oriented matroid types.
        """
        self._from = fromOM
        self._to = toType
        if groundset:
            self._groundset = groundset
        else:
            self._groundset = self._from.groundset()

        if self._to not in OrientedMatroids.keys:
            raise ValueError("{} is not a key in OrientedMatroids.keys".format(self._to))

    def map(self):
        f = self._from.key
        t = self._to

        met = getattr(self,f+'_to_'+t,False)
        if met:
            return met()
        else:
            t = (f, t, f, t)
            raise AttributeError("No map from {} oriented matroids to {} oriented matroids exists. Please create a function OrientedMatroid.{}_to_{}()".format(*t))

    def real_hyperplane_arrangement_to_covector(self):
        """
        Return a covector oriented matroid from hyperplane arrangement oriented matroid

        EXAMPLES::
            sage: from oriented_matroids import OrientedMatroid
            sage: from oriented_matroids.oriented_matroid_mapper import oriented_matroid_mapper
            sage: A = hyperplane_arrangements.braid(3)
            sage: M = OrientedMatroid(A); M
            Hyperplane arrangement oriented matroid of rank 2
            sage: oriented_matroid_mapper(M,'covector')
            Covector oriented matroid of rank 3
        
        """

        arrangement = self._from.arrangement()
        covectors = []
        # Grab all sign-vectors
        for f in arrangement.closed_faces():
            covectors.append(f[0])
        return OrientedMatroid(covectors, key='covector', groundset=self._groundset)


def oriented_matroid_mapper(fromOM, toOM):
    OMM = OrientedMatroidMapper(fromOM, toOM)
    return OMM.map()
