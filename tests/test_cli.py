import sys

import timetagger_cli
from timetagger_cli import __main__
from pytest import raises
from _common import run_tests


def _raise_RuntimeError():
    raise RuntimeError()


def test_cli():
    main = __main__.main

    lines = []
    __main__.print = lambda *args: lines.append(" ".join(str(x) for x in args) + "\n")

    # Empty args is help
    main([])
    text = "\n".join(lines)
    lines.clear()
    for x in ["timetagger", "CLI", "version", "setup", "status", "start", "stop"]:
        assert x in text

    # Other common ways to get help
    for arg in ["help", "-h", "--help"]:
        main([arg])
        assert "\n".join(lines) == text
        lines.clear()

    # No args uses sys.argv
    sys.argv = ["", "version"]
    main()
    assert timetagger_cli.__version__ in lines[0]
    lines.clear()

    # Invalid command
    with raises(BaseException):  # RunTimeError is turned into SystemExit
        main(["notavalidcommand"])

    # Error in command
    timetagger_cli.core.request = lambda method, path, body=None: _raise_RuntimeError()
    with raises(BaseException):  # RunTimeError is turned into SystemExit
        main(["status"])

    # Other errors fall through
    with raises(TypeError):
        main(["help", "help_func_has_no_args"])

    # Run one command through to a function
    response = {"records": []}
    timetagger_cli.core.request = lambda method, path, body=None: response
    main(["status"])


if __name__ == "__main__":
    run_tests(globals())
