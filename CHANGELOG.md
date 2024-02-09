# Change Log

All notable changes will be made in this file.

## [0.1.0] - 2024-02-09

### Added

- (#18) Implemented Cocircuits and covectors.
- (#14) Added some additional examples to ensure tests catch potential errors.

### Changed

- (#22) Updated the documentation to be more complete.
- (#12) Altered it so that the `to_xxx()` functions are encapsulated in the function `change_type()`.
- (#2) Updated package to fit into up to date methods for making packages.
- (#1) Restructed the OrientedMatroids class. In particular:
    - Removed the category implementation and structured based off the matroid implementation.
    - There is now an `AbstractOrientedMatroid` class which handles the abstract methods and everything pulls from here.

### Fixed

- (#15) Fixed the groundset error bug.


## [0.0.2] - 2020-12-15

### Added

- Can now add point configurations

### Changed

- All oriented matroids can now contain covectors, vectors, circuits and cocircuits
- Restructured oriented matroids to fit new schema

### Fixed

- Matroid function now properly brings correct matroid
- Rank function now properly displays correct rank

## [0.0.1] - 2019-07-12

### Added

- The three main types of oriented matroids:

    - Circuit
    - Covector
    - Vector

- Made elements viewable as signed subsets and vectors
- Hyperplane arrangements using covectors
- Digraphs using circuits

### Changed

### Fixed
