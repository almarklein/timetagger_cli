from argparse import Namespace
import time

from timetagger_cli import core
from _common import run_tests


def test_print_records():
    lines = []
    core.print = lambda *args: lines.append(" ".join(str(x) for x in args) + "\n")

    now = time.time()

    records = [
        dict(key="1", t1=now, t2=now + 30, mt=now, st=0, ds="foo"),
        dict(key="2", t1=now, t2=now + 60, mt=now, st=0, ds="bar"),
        dict(key="3", t1=now, t2=now + 3600, mt=now, st=0, ds="spam"),
        dict(key="4", t1=now, t2=now + 43200, mt=now, st=0),
    ]
    core.print_records(records)

    text = "\n".join(lines)

    assert len(lines) == len(records) + 1
    for r in records:
        assert r.get("ds", "") in text

    assert "0:00" in text
    assert "0:01" in text
    assert "1:00" in text
    assert "12:00" in text


def test_setup():
    core.open_with_os_default = lambda p: None

    lines = []
    core.print = lambda *args: lines.append(" ".join(str(x) for x in args) + "\n")

    core.setup()

    assert len(lines) == 2


def test_start():
    response = {"records": []}
    core.request = lambda method, path, body=None: response

    lines = []
    core.print = lambda *args: lines.append(" ".join(str(x) for x in args) + "\n")

    core.start(Namespace(description="foobar"))

    text = "\n".join(lines)
    lines.clear()
    assert "foobar" in text
    assert "started" in text.lower()
    assert "and stopped" not in text.lower()

    response["records"].append(dict(t1=3, t2=3))
    core.start(Namespace(description="foobar"))

    text = "\n".join(lines)
    lines.clear()
    assert "foobar" in text
    assert "started" in text.lower()
    assert "and stopped" in text.lower()


def test_stop():
    response = {"records": []}
    core.request = lambda method, path, body=None: response

    lines = []
    core.print = lambda *args: lines.append(" ".join(str(x) for x in args) + "\n")

    core.stop()

    text = "\n".join(lines)
    lines.clear()
    assert "no running" in text.lower()
    assert "stopped" not in text.lower()

    response["records"].append(dict(t1=3, t2=3))
    core.stop()

    text = "\n".join(lines)
    lines.clear()
    assert "no running" not in text.lower()
    assert "stopped" in text.lower()


def test_status():
    now = int(time.time())

    records = [
        dict(key="1", t1=now - 60, t2=now, mt=now, st=0, ds="foo"),
        dict(key="1", t1=now, t2=now + 60, mt=now, st=0, ds="foo"),
        dict(key="2", t1=now - 3600, t2=now, mt=now, st=0, ds="bar"),
        dict(key="3", t1=now - 3600, t2=now, mt=now, st=0, ds="HIDDEN removed"),
        dict(key="4", t1=now - 3600, t2=now, mt=now, st=0, ds="not removed HIDDEN "),
    ]

    response = {"records": records}
    core.request = lambda method, path, body=None: response

    lines = []
    core.print = lambda *args: lines.append(" ".join(str(x) for x in args) + "\n")

    core.status()

    text = "\n".join(lines)
    lines.clear()
    assert "today:" in text and "this week:" in text
    assert "running: n/a" in text.lower()
    assert "not removed HIDDEN" in text
    assert "HIDDEN removed" not in text

    response["records"].append(dict(t1=now, t2=now))
    core.status()

    text = "\n".join(lines)
    lines.clear()
    assert "today:" in text and "this week:" in text
    assert "running: 0:00" in text.lower()

    response["records"].append(dict(t1=now, t2=now))
    response["records"].append(dict(t1=now, t2=now))
    core.status()

    text = "\n".join(lines)
    lines.clear()
    assert "today:" in text and "this week:" in text
    assert "3 running" in text.lower()


if __name__ == "__main__":
    run_tests(globals())
