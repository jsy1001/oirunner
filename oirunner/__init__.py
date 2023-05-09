"""The oirunner package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("oirunner")
except PackageNotFoundError:
    # package is not installed
    __version__ = "[not installed]"
