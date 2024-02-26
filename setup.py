import os
import sys
from setuptools import setup, find_packages
from codecs import open  # To open the README file with proper encoding
from setuptools.command.test import test as TestCommand  # for tests


# Get information from separate files (README, VERSION)
def readfile(filename):
    with open(filename,  encoding='utf-8') as f:
        return f.read()


# For the tests
class SageTest(TestCommand):
    def run_tests(self):
        errno = os.system("sage -t --force-lib oriented_matroids")
        if errno != 0:
            sys.exit(1)


setup(
    version=readfile('VERSION').strip(),
    packages=find_packages(),
    cmdclass={'test': SageTest}  # adding a special setup command for tests
)
