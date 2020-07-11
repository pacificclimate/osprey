#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()
CHANGES = open(os.path.join(here, "CHANGES.rst")).read()
REQUIRES_PYTHON = ">=3.5.0"

about = {}
with open(os.path.join(here, "osprey", "__version__.py"), "r") as f:
    exec(f.read(), about)

reqs = [line.strip() for line in open("requirements.txt")]
dev_reqs = [line.strip() for line in open("requirements_dev.txt")]

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Scientific/Engineering :: Atmospheric Science",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
]

setup(
    name="osprey",
    version=about["__version__"],
    description="A Web Processing Service for Climate Data Analysis.",
    long_description=README + "\n\n" + CHANGES,
    long_description_content_type="text/x-rst",
    author=about["__author__"],
    author_email=about["__email__"],
    url="https://github.com/nikola-rados/osprey",
    python_requires=REQUIRES_PYTHON,
    classifiers=classifiers,
    license="GNU General Public License v3",
    keywords="wps pywps birdhouse osprey",
    packages=find_packages(),
    include_package_data=True,
    install_requires=reqs,
    extras_require={"dev": dev_reqs,},  # pip install ".[dev]"
    entry_points={"console_scripts": ["osprey=osprey.cli:cli",]},
)
