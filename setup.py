import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand  # for tests


# For the tests
class SageTest(TestCommand):
    def run_tests(self):
        errno = os.system("sage -t --force-lib oriented_matroids")
        if errno != 0:
            sys.exit(1)


setup(
    version='0.1.1',
    packages=find_packages(),
    cmdclass={'test': SageTest},  # adding a special setup command for tests
)
