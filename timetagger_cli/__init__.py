"""
Track your time from the command-line, a CLI for https://timetagger.app.
"""

__version__ = "21.5.1"

version_info = tuple(map(int, __version__.split(".")))

from .core import app, setup, status, start, stop  # noqa
