import pytest
import copy
import logging

import raxolotl.configuration as conf
from raxolotl.exceptions import ConfigurationError

LOGGER = logging.getLogger(__name__)

class TestRaxolotlTarget:

    DEFAULTS = {
        'snapshots': 23,
        'retries': 5,
        'fsroot': '/',
        'exclude': []
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
