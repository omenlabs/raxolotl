import pytest
import copy
import logging

import raxolotl.configuration as conf
from raxolotl.exceptions import *

LOGGER = logging.getLogger(__name__)

BAD_CONFIG = """
defaults:
  - target: f
targets:
  asdf: {}
"""

GOOD_CONFIG = """
defaults:
  exclude:
   - /dev
   - /sys
  snapshots: 8
  retries: 8
targets:
  mailserver:
    hostname: mail.local
    datastore: tank/backups/mail
"""

class TestRaxolotlConfiguration:


    @pytest.fixture(scope='session')
    def good_config_file(self, tmpdir_factory):

        good = tmpdir_factory.mktemp('data').join('good.yaml')

        with open(str(good), "w") as f:
            f.write(GOOD_CONFIG)

        return good

    @pytest.fixture(scope='session')
    def bad_config_file(self, tmpdir_factory):

        bad = tmpdir_factory.mktemp('data').join('bad.yaml')

        with open(str(bad), "w") as f:
            f.write(BAD_CONFIG)

        return bad

    @pytest.fixture(scope='session')
    def junk_yaml_file(self, tmpdir_factory):

        fn = tmpdir_factory.mktemp('data').join('garbage.yaml')
        with open(str(fn), "w") as f:
            f.write("name: { 'asdf':")

        return fn

    def test_config_not_found(self):

        config = conf.RaxolotlConfiguration()
        with pytest.raises(ConfigurationNotFound):
            config.load_configuration("asdfasdfasdf.yaml")

    def test_bad_yaml(self, junk_yaml_file):

        config = conf.RaxolotlConfiguration()
        with pytest.raises(ConfigurationParseError):
            config.load_configuration(str(junk_yaml_file))

    def test_good_config(self, good_config_file):
        config = conf.RaxolotlConfiguration()
        config.load_configuration(str(good_config_file))

        assert 'mailserver' in config.targets

    def test_bad_config(self, bad_config_file):
        config = conf.RaxolotlConfiguration()

        with pytest.raises(ConfigurationError):
            config.load_configuration(str(bad_config_file))

class TestRaxolotlTarget:

    DEFAULTS = {
        'snapshots': 23,
        'retries': 5,
        'fsroot': '/',
        'exclude': [],
        'user': 'root'
    }

    BASE_SETTINGS = {
        'datastore': "tank/backup",
        'hostname': "localhost"
        }

    def test_missing_value(self):

        settings = copy.copy(self.BASE_SETTINGS)
        settings.pop('hostname')

        with pytest.raises(ConfigurationError):
            conf.RaxolotlTarget("test", settings, self.DEFAULTS)

    def test_normalization(self):

        target = conf.RaxolotlTarget("test", self.BASE_SETTINGS, self.DEFAULTS)

        for key,value in self.DEFAULTS.iteritems():
            assert getattr(target, key) == value

    def test_exludes_merge(self):

        defaults = copy.copy(self.DEFAULTS)
        settings = copy.copy(self.BASE_SETTINGS)

        exclude = ['/dev', '/sys', '/nfs', '/proc']
        LOGGER.info("Test harness exclude: %s", exclude)

        defaults['exclude'] = exclude[:2]
        settings['exclude'] = exclude[2:]

        target = conf.RaxolotlTarget("test", settings, defaults)
        LOGGER.info("Target exclude: %s", target.exclude)
        for i in target.exclude:
            assert i in exclude

        for i in exclude:
            assert i in target.exclude

    def test_properties(self):
        """Since we are a thin wrapper around a dictionary with properties
        mostly for docstrings, check that they all exist """

        target = conf.RaxolotlTarget("test", self.BASE_SETTINGS, self.DEFAULTS)

        for key in target._settings:
            assert hasattr(target, key)
