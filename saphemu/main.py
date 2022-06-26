#!/usr/bin/env python3

import argparse

from saphemu.auth.login_server import LoginServer
from saphemu.common.log import LOG
from saphemu.db.database_client import DatabaseClient
from saphemu.world.world_server import WorldServer

MODULES = {"login": LoginServer, "world": WorldServer, "db": DatabaseClient}


def main():
    LOG.info("SaphEmu - WoW 1.1.2.4125 Sandbox Server - Shgck 2016")

    argparser = argparse.ArgumentParser()
    argparser.add_argument("module", type=str, help="module to start")
    args = argparser.parse_args()

    if args.module in MODULES:
        module_class = MODULES[args.module]
        module = module_class()
        module.start()
    else:
        print("Unknown module:", args.module)


if __name__ == "__main__":
    main()
