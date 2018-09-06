from pbr.version import VersionInfo

_v = VersionInfo('oirunner').semantic_version()
__version__ = _v.release_string()
