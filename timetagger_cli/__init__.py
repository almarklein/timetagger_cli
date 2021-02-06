"""
Track your time from the command-line.
A CLI for TimeTagger (https://timetagger.app
"""

__version__ = "21.2.1"

version_info = tuple(map(int, __version__.split(".")))

from ._cli import main  # noqa
