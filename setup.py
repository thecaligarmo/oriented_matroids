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
    name="oriented_matroids",
    description='Oriented matroids for sagemath',
    version=readfile('VERSION').strip(),
    long_description=readfile('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/thecaligarmo/oriented_matroids',
    author='Aram Dermenjian',
    author_email='aram.dermenjian.math@gmail.com',
    project_urls={
        'Bug Tracker': 'https://github.com/thecaligarmo/oriented_matroids/issues',
    },
    license='GPLv3+',  # This should be consistent with the LICENCE file
    python_requires='>=3.8',
    # classifiers list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    keywords="SageMath packaging",
    packages=find_packages(),
    cmdclass={'test': SageTest},  # adding a special setup command for tests
    setup_requires=['sage-package'],
    install_requires=['sage-package', 'sphinx'],
)
