from setuptools import setup, find_packages
from distutils.util import convert_path

import os
from os import listdir
from os.path import isfile, join


main_ns = {}
ver_path = convert_path('aiogoogle/__version__.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

mypath = os.path.dirname(os.path.abspath(__file__))
print([f for f in listdir(mypath) if isfile(join(mypath, f))])


with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

with open("test_requirements.txt", "r") as f:
    test_requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name=main_ns['__name__'],
    version=main_ns['__version__'],
    author=main_ns['__author__'],
    author_email=main_ns['__author_email__'],
    license=main_ns['__license__'],
    description=main_ns['__description__'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    tests_require=test_requirements,
    url=main_ns["__url__"],
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    extras_require={"curio_asks": ["asks", "curio"], "trio_asks": ["asks", "trio"]},
)
