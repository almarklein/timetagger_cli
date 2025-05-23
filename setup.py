import re

from setuptools import setup


with open("timetagger_cli/__init__.py") as fh:
    VERSION = re.search(r"__version__ = \"(.*?)\"", fh.read()).group(1)

with open("requirements.txt") as fh:
    runtime_deps = [x.strip() for x in fh.read().splitlines() if x.strip()]

short_description = "Track your time from the command-line."

long_description = """
# TimeTagger CLI

*Track your time from the command-line.*

[TimeTagger](https://timetagger.app) is an open source time tracker with a focus on a simple and interactive user experience.

This is a CLI that allows users to track their time from the terminal.
This can be used when running a TimeTagger server locally, or by
connecting with https://timetagger.app.

Just setup with the API token, and start tracking!

More info on Github: https://github.com/almarklein/timetagger_cli
"""


setup(
    name="timetagger_cli",
    version=VERSION,
    author="Almar Klein",
    author_email="",
    license="MIT",
    url="https://github.com/almarklein/timetagger_cli",
    keywords="time, tracker, CLI, terminal",
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms="any",
    python_requires=">=3.9",
    install_requires=runtime_deps,
    packages=["timetagger_cli"],
    entry_points={"console_scripts": ["timetagger = timetagger_cli.__main__:main"]},
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
