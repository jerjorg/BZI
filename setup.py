#!/usr/bin/env python
# This module will allow you to pip install BZI.
# Use pip install -e . in the root directory.
try:
    from setuptools import setup
    args = {}
except ImportError:
    from distutils.core import setup
    print("""\*** WARNING: setuptools is not found.  Using distutils...""")

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

from os import path
setup(name='bzi_3D',
      version='0.3.3',
      description='Brillouin zone integration.',
      long_description= "" if not path.isfile("README.md") else read_md('README.md'),
      author='Jeremy Jorgensen',
      author_email='jerjorg@gmail.com',
      url='https://github.com/jerjorg/bzi_3D',
      license='MIT',
      setup_requires=['pytest-runner',],
      tests_require=['pytest', 'python-coveralls'],
      install_requires=[
          "argparse",
          "termcolor",
          "numpy",
          "matplotlib",
          "phenum",
          "pandas",
          "xarray",
          "scipy"
      ],
      packages=['bzi_3D'],
      package_data={'bzi_3D': []},
      include_package_data=True,
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Operating System :: MacOS',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
      ],
     )
