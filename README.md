# Saph-Emu

This is a World of Warcraft 1.1.2.4125 tiny server emulator, written in Python,
which tries to remain small, clean and understandable. The goal is to handle
several player and basic stuff like chat and groups to have some fun with old
school exploration techniques. This project is meant to continue education on
Python enthusiast and a continues project where we fruitition development on a
common ground WoW. This project has no intention to be a serious project, only a
foundation of a game we all love.

There are very few sanity checks beside basic auth, and almost nothing that a
client wouldn't do is checked for. It is also not meant to be an efficient
implementation. It is in Python, and nothing is done to circumvent the GIL.

This is a forked project to attempt to continue the journey that Durator-Emu has left
for us.

Use it to have fun exploring with a few friends, that's all.

## Installation

Dependencies:

- Python 3.8+
- MySQL
- Peewee, the Python ORM used
- Python MySQL driver
- PyShgck

### Python 3.8+

Get that from their website.

### MySQL

Get a community package from their website, anything slightly recent should be
fine. Once the MySQL server is running, you need to setup a database and an
account to access this database.

Quick MySQL database setup:

- CREATE DATABASE saphemu;
- CREATE USER 'saphemu'@'%' IDENTIFIED BY 'saphemu'
- GRANT ALL PRIVILEGES ON saphemu.\* TO 'saphemu'@'%' IDENTIFIED BY 'saphemu';

Feel free to use other credentials (but update the database code configuration),
and to narrow the hostname to something more private than a full wildcard.

### Peewee

Available in PyPI:

```bash
pip install peewee
```

### Python MySQL driver

You only need one of them, preferably PyMySQL because that's the one I use, but
both are available in PyPI:

````bash
pip install pymysql
``` cc

## Configuration

Configure the database and create an account with the database client

```bash
cd Saphemu
python3 -m saphemu.main db
# use the commands 'install' and 'account'
````

Then just use `start.bat`, or manually start the login and world servers in
different consoles:

```bash
python3 -m saphemu.main login
python3 -m saphemu.main world
```

## Documentation

Some related projects and documentation that I used, first for Vanilla (mostly
1.12):

- [WoWCore](https://github.com/RomanRom2/WoWCore/)
- [MangosClassic](https://github.com/cmangos/mangos-classic)
- [Ember](https://github.com/EmberEmu/Ember)
- [Miceiken's server](http://git.clusterbrain.net/miceiken/WoWClassicServer)

More recent but still interesting sources:

- [Mangos wiki](https://getmangos.eu/wiki/Reference%20Information)
- [ArcEmu wiki](http://www.arcemu.org/wiki/Packets)
