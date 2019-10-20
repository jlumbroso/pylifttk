import os
from setuptools import setup, find_packages

PACKAGE_NAME = "pylifttk"

# The text of the README file
README = open("README.md").read()

# Get the version number without importing our package
# (which would trigger some ImportError due to missing dependencies)

version_contents = {}
with open(os.path.join(PACKAGE_NAME, "version.py")) as f:
    exec(f.read(), version_contents)

# This call to setup() does all the work
setup(
    name=PACKAGE_NAME,
    version=version_contents["__version__"],
    description="Python utility toolkit for Princeton CS's LIFT.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jlumbroso/pylifttk",
    author="Jérémie Lumbroso",
    author_email="lumbroso@cs.princeton.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    install_requires=[
        "bs4",
        "codepost",
        "confuse",
        "python-dateutil",
        "pywsse",
        "PyYAML",
        "requests",
        "six",
        # "better_exceptions",
        # "blessings",
        # "colorama",
        # "eliot",
    ],
    include_package_data=True,
)
