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

class OrientedMatroidMapper:

    def __init__(self,fromOM,toOM):
        r"""
        Initialize our two desired oriented matroid types.
        """
        self._from = fromOM
        self._to = toOM

    def map(self):
        fromclass = self._from.__class__.__name__
        toclass = self._to.__class__.__name__
        fc = fromclass.lower()
        tc = toclass.lower()
        fromtype = fc[:fc.find('orientedmatroid')]
        totype = tc[:tc.find('orientedmatroid')]

        met = getattr(self,fromtype+'_to_'+totype,False)
        if met:
            return met()
        else:
            t = (fromclass, toclass, fromtype, totype)
            raise AttributeError("No map from {} to {} exists. Please create a function OrientedMatroid.{}_to_{}()".format(*t))


def oriented_matroid_mapper(fromOM, toOM):
    OMM = OrientedMatroidMapper(fromOM, toOM)
    return OMM.map()
