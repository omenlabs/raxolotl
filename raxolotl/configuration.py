""" Configuration Handlers """

import logging

# third party
import yaml

# module
from raxolotl.exceptions import * # pylint: disable=wildcard-import

class RaxolotlConfiguration(object):
    """ Load the configuration """

    REQUIRED_SECTIONS = ['defaults', 'targets']

    def __init__(self):

        self._targets = {}
        self._defaults = {}
        self._logger = logging.getLogger(__name__)

    @staticmethod
    def _merge_defaults(target, defaults):
        """ Merge in defaults if they don't exist in target """

        # Nothing fancy
        for key in defaults:
            if not key in target:
                target[key] = defaults[key]

    def load_configuration(self, filename):
        """ Load a configuration and initialized the objects """

        try:
            with open(filename) as cfg:
                try:
                    config = yaml.load(cfg)
                except yaml.YAMLError:
                    self._logger.exception("Failed to parse configuration file %s",
                                           filename)
                    raise ConfigurationParseError("Failed to parse configuration file, check logs")

        except IOError:
            self._logger.exception("Failed to open configuration file %s", filename)
            raise ConfigurationNotFound("Failed to open configuration file, check logs")

        # Basic santiy checks
        for section in self.REQUIRED_SECTIONS:
            if not section in config:
                message = ("Section '{}' does not exists in configuration {}"
                          ).format(section, filename)
                self._logger.error(message)
                raise ConfigurationError(message)

            if not isinstance(config[section], dict):
                message = ("Section '{}' must be a dictionary in configuration {}"
                          ).format(section, filename)
                self._logger.error(message)
                raise ConfigurationError(message)


        self._defaults = config['defaults']
        # Populate the targets
        for target, settings in config['targets'].iteritems():
            self._merge_defaults(settings, target)
            self._targets[target] = RaxolotlTarget(target, settings)


    @property
    def targets(self):
        """ Dictionary of RaxolotlTarget objects """
        return self._targets


class RaxolotlTarget(object):
    """ Target Configuration """

    REQUIRED_SETTINGS = ['datastore', 'hostname', 'fsroot', 'snapshots']

    def __init__(self, name, settings):

        self._logger = logging.getLogger(__name__)

        for key in self.REQUIRED_SETTINGS:
            if not key in settings:
                message = "Target '{}' does not contain requried setting '{}'".format(name, key)
                self._logger.error(message)
                raise ConfigurationError(message)

        self._name = name
        self._settings = settings

    @property
    def name(self):
        """ Human name of this target """
        return self._name

    @property
    def datastore(self):
        """ ZFS datastore we are using to store snapshots """
        return self._settings['datastore']

    @property
    def snapshots(self):
        """ How many snapshots to keep around """
        return self._settings['snapshots']

    @property
    def hostname(self):
        """ Hostname to rsync from """
        return self._settings['hostname']

    @property
    def fsroot(self):
        """ Where to start backing up from on remote host """
        return self._settings['fsroot']

    @property
    def exclude(self):
        """ Paths to exclude """
        return self._settings.get('exclude')
