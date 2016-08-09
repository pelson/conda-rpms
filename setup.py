#!/usr/bin/env python

from __future__ import print_function

import os
from setuptools import setup


NAME = 'conda_rpms'
DIR = os.path.abspath(os.path.dirname(__file__))


def extract_packages():
    packages = []
    root = os.path.join(DIR, NAME)
    offset = len(os.path.dirname(root)) + 1
    for dpath, dnames, fnames in os.walk(root):
        if os.path.exists(os.path.join(dpath, '__init__.py')):
            package = dpath[offset:].replace(os.path.sep, '.')
            packages.append(package)
    return packages


def extract_version():
    version = None
    fname = os.path.join(DIR, NAME, '__init__.py')
    with open(fname) as fin:
        for line in fin:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation.
                break
    return version


def read(*parts):
    result = None
    fname = os.path.join(DIR, *parts)
    if os.path.isfile(fname):
        with open(fname, 'rb') as fh:
            result = fh.read().decode('utf-8')
    return result


def extract_description():
    description = read('README.rst')
    if description is None:
        description = 'conda-rpms'
    return description


def extract_requirements():
    require = read('requirements.txt')
    return [r.strip() for r in require.splitlines()]


setup_args = dict(
    name             = NAME,
    version          = extract_version(),
    description      = 'conda-rpms',
    long_description = extract_description(),
    platforms        = ['Linux', 'Mac OS X', 'Windows'],
    license          = 'BSD 3-clause',
    packages         = extract_packages(),
    classifiers      = [
        'License :: OSI Approved :: BSD License',
        'Development Status :: 1 - Planning Development Status',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries'],
    install_requires = extract_requirements(),
    test_suite = '{}.tests'.format(NAME),
)


if __name__ == "__main__":
    setup(**setup_args)
