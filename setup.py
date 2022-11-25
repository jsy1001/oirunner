"""Setup module for oirunner."""

from setuptools import setup, find_packages
import os.path

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="oirunner",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Tool to reconstruct images from optint data using BSMEM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jsy1001/oirunner",
    author="John Young",
    author_email="jsy1001@cam.ac.uk",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=["docs", "tests"]),
    install_requires=["numpy", "astropy", "scipy"],
    entry_points={
        "console_scripts": [
            "makesf=oirunner.makesf.__main__:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/jsy1001/oirunner/issues",
    },
)
