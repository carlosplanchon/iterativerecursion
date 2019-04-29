#!/usr/bin/env python3

from setuptools import setup
from pathlib import Path

readme = Path("README.md").read_text()


setup(
    name="iterativerecursion",
    packages=["iterativerecursion"],
    version="0.1",
    license="GPL3",
    description="Python3 module to simulate recursion with iteration.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Carlos A. Planchón",
    author_email="bubbledoloresuruguay2@gmail.com",
    url="https://github.com/carlosplanchon/iterativerecursion",
    download_url="https://github.com/carlosplanchon/"
        "iterativerecursion/archive/v0.1.tar.gz",
    keywords=["iterative", "recursion"],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
