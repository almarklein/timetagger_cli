import os
import time

from timetagger_cli import utils
from _common import run_tests


def test_generate_uid():
    uid = utils.generate_uid()
    assert isinstance(uid, str)
    assert len(uid) > 7

    n = 100
    uids = set(utils.generate_uid() for i in range(n))
    assert len(uids) == n  # could fail if we're VERY unlucky


def test_user_config_dir():
    path1 = utils.user_config_dir()
    assert isinstance(path1, str)
    assert os.path.isdir(path1)

    path2 = utils.user_config_dir("timetagger_cli")
    assert isinstance(path2, str)
    assert os.path.isdir(path2)

    assert path1 != path2


def test_readable_time():
    x = utils.readable_time(time.time())
    assert isinstance(x, str)
    assert x.count("-") == 2
    assert x.count(":") == 1
    assert len(x) == 16


def test_readable_duration():
    assert utils.readable_duration(0) == "0:00"
    assert utils.readable_duration(29) == "0:00"
    assert utils.readable_duration(31) == "0:01"
    assert utils.readable_duration(60 + 29) == "0:01"
    assert utils.readable_duration(60 + 29) == "0:01"
    assert utils.readable_duration(42 * 3600 + 14 * 60) == "42:14"


if __name__ == "__main__":
    run_tests(globals())
