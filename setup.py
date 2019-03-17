import codecs
import re

import os
from setuptools import (
    setup,
    find_packages,
)


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


requires = [
    "requests==2.20.0",
    "jsonschema==2.6.0",
]

tests_require = [
    "pytest",
    "py_fake_server",
    "pytest-cov",
]

setup(
    name="papiline",
    version=find_version("papiline", "__init__.py"),
    description="Build your own requests pipeline!",
    url="https://github.com/altager/papiline",
    author="Sergey Ovodov",
    author_email="orion.tide@gmail.com",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=requires,
    tests_require=tests_require,
    setup_requires=["pytest-runner"],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
