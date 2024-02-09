# Oriented Matroids

This package contains an oriented matroid implementation for sagemath.

## Current version

The current version is 0.1.0 and is compatible with sagemath 10.0. It is in beta and is open for testing from others.

**NOTE:** This package will be integrating into SageMath directly. If you see any errors while using this please, open an issue and let us know so we can correct it.


## Installation

### Installation from Pypi
Use `pip` to install the package:

```
$ sage -pip install --index-url https://test.pypi.org/simple/ --no-deps oriented_matroids
```

### Local install from source
Download the source from the git repository:
```
$ git clone https://github.com/thecaligarmo/oriented_matroids.git
```

Change to the root directory and run:
```
$ sage -pip install .
```

For convenience this package contains a makefile with this and other often used commands. Should you wish too, you can use the shorthand:

```
$ make install
```

Note that you might need to alter the make file in order for this to run properly if your sage is located in another directory.

### Common errors

If you get "SSL" errors, try the fixes found on: [ask sagemath](https://ask.sagemath.org/question/51130/ssl-error-using-sage-pip-install-to-download-a-package/)

## Using the package after install
After install, you can start sage and run the following command to have all methods available:
```
from oriented_matroids import *
```

## Uninstall
To uninstall the package you can run the following command
```
$ sage -pip uninstall oriented_matroids
```

Alternatively, if you installed locally and want to uninstall using `make`, you can run:
```
$ make uninstall
```
