from configparser import ConfigParser
from os.path import dirname, join, normpath

ROOT_DIR = normpath(join(dirname(__file__), "../"))
CONFIG_DIR = join(ROOT_DIR, "config")
SAPHEMU_CONFIG = join(CONFIG_DIR, "saphemu.ini")

ALL_CONFIG_FILES = [SAPHEMU_CONFIG]


def _load_config():
    global CONFIG
    CONFIG = ConfigParser()
    CONFIG.read(ALL_CONFIG_FILES)

    global DEBUG
    DEBUG = CONFIG.getboolean("general", "debug")


# Static config object, loaded when the module is imported.
CONFIG = None
DEBUG = False

_load_config()
