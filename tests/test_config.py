import os

from timetagger_cli import config
from pytest import raises
from _common import run_tests


def test_prepare_config_file():
    filename = config.prepare_config_file()
    assert isinstance(filename, str)
    assert os.path.isfile(filename)


def test_load_config():
    d = config.load_config()
    assert isinstance(d, dict)
    assert "api_url" in d
    assert "api_token" in d
    assert "ssl_verify" in d


def test_load_config_fail():
    # Use different config file for tests
    config.config_fname = "test_config.txt"

    # Get filename
    filename = config.prepare_config_file()

    # No file, no glory
    os.remove(filename)
    with raises(RuntimeError):
        config.load_config()

    # But revivable!
    config.prepare_config_file()
    assert config.load_config()

    # Get the original text
    with open(filename, "rb") as f:
        ori_text = f.read().decode()

    # Empty file, no glory either
    with open(filename, "wb") as f:
        f.write(b"")
    with raises(RuntimeError):
        config.load_config()

    # But still revivable!
    config.prepare_config_file()
    assert config.load_config()

    # File without url
    with open(filename, "wb") as f:
        text = ori_text.replace("api_url", "xx_url")
        f.write(text.encode())
    with raises(RuntimeError):
        config.load_config()

    # File without token
    with open(filename, "wb") as f:
        text = ori_text.replace("api_token", "xx_token")
        f.write(text.encode())
    with raises(RuntimeError):
        config.load_config()

    # File without ssl_verify
    with open(filename, "wb") as f:
        text = ori_text.replace("ssl_verify", "xxx_verify")
        f.write(text.encode())
    assert config.load_config()

    # But ok to add other stuff ...
    with open(filename, "wb") as f:
        text = ori_text + "\n# some comments\nbar = 42\n"
        f.write(text.encode())
    assert config.load_config()

    # URL's have certain rules
    with open(filename, "wb") as f:
        text = ori_text.replace("http", "xxxx")
        f.write(text.encode())
    with raises(RuntimeError):
        config.load_config()

    # Reset
    with open(filename, "wb") as f:
        f.write(ori_text.encode())


if __name__ == "__main__":
    run_tests(globals())
