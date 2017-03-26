import configparser
from io import StringIO

import pytest

from pblog import cli


def test_reads_env():
    env_file = StringIO("""
[pblog]
env = default

[pblog:default]
url = http://example.org/api
username = Mr Ham
""")

    env = cli.parse_env(env_file)

    assert env.name == 'default'
    assert env.url == 'http://example.org/api'
    assert env.username == 'Mr Ham'


def test_overrides_env():
    env_file = StringIO("""
[pblog]
env = default

[pblog:not-default]
url = http://example.org/api
username = Mr Ham
""")

    env = cli.parse_env(env_file, env='not-default')

    assert env.name == 'not-default'
    assert env.url == 'http://example.org/api'
    assert env.username == 'Mr Ham'


def test_pblog_section_not_found():
    env_file = StringIO("""
[pblog:default]
""")

    with pytest.raises(cli.EnvError):
        cli.parse_env(env_file)


def test_pblog_values_not_found():
    env_file = StringIO("[pblog:default]")

    with pytest.raises(KeyError):
        cli.parse_env(env_file, env='default')


def test_not_an_ini_fil():
    env_file = StringIO("This is not an ini file")

    with pytest.raises(configparser.Error):
        cli.parse_env(env_file)
