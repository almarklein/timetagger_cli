import os
import sys

import toml

from .utils import user_config_dir

initial_config_text = """
# This is the TimeTagger CLI configuration, in toml format.
# Clear or remove this file to reset to factory defaults.

# Set the base API URL, for example:
# - "https://timetagger.app/api/v2/"  -> default
# - "http://localhost/timetagger/api/v2/"  -> a local server
api_url = "https://timetagger.app/api/v2/"

# Set your API token.
# Go to the account page, copy the token, paste it here (between the quotes).
api_token = ""

# If you're self-hosting, you might need to set your own self-signed certificate or disable the verification of SSL certificate.
# Disabling the certificate verification is a potentially risky action that might expose your application to attacks.
# You can set the path to a self signed certificate for verification and validation:
# - ssl_verify = "path/to/certificate"
# For more information, visit: https://letsencrypt.org/docs/certificates-for-localhost/
ssl_verify = true
""".lstrip().replace(
    "\r\n", "\n"
)

if sys.platform.startswith("win"):
    initial_config_text.replace("\n", "\r\n")


config_fname = "config.txt"


def load_config():
    """Load the config file and validate contents."""
    filename = os.path.join(user_config_dir("timetagger_cli"), config_fname)
    if not os.path.isfile(filename):
        raise RuntimeError("Config not set, run 'timetagger setup' first.")

    with open(filename, "rb") as f:
        config = toml.loads(f.read().decode())

    if "api_url" not in config:
        raise RuntimeError("No api_url set in config. Run 'timetagger setup' to fix.")
    if not config["api_url"].startswith(("http://", "https://")):
        raise RuntimeError(
            "The api_url must start with 'http://' or 'https://'. Run 'timetagger setup' to fix."
        )
    if "api_token" not in config:
        raise RuntimeError("No api_token set in config. Run 'timetagger setup' to fix.")
    if "ssl_verify" not in config:
        config |= {"ssl_verify": True}
    return config


def prepare_config_file():
    filename = os.path.join(user_config_dir("timetagger_cli"), config_fname)

    # If the config file is empty or does not exist, we write a default text
    try:
        if os.path.isfile(filename):
            with open(filename, "rb") as f:
                text = f.read().strip()
            if not text:
                with open(filename, "wb") as f:
                    f.write(initial_config_text.encode())
        else:
            with open(filename, "wb") as f:
                f.write(initial_config_text.encode())
        # Config file contains user secret so it should not be readable to others
        os.chmod(filename, 0o640)
    except Exception as err:  # pragma: no cover
        print(f"Could not prepare config file: {err}")

    return filename
