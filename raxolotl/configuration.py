""" Configuration Handlers """

import logging

# third party
import yaml
import cerberus

# module
from raxolotl.exceptions import * # pylint: disable=wildcard-import

class RaxolotlConfiguration(object):
    """ Load the configuration """

    # We use this mainly to specify the universal defaults
    # Target validation is done on a per target basis and uses
    # the defaults defined here
    _SCHEMA = {
        'defaults': {
            'type': 'dict',
            'schema': {
                'retries': {
                    'type': 'integer',
                    'default': 5
                },
                'snapshots': {
                    'type': 'integer',
                    'default': 23
                }
            },
            'targets': {
                'type': 'dict',
                'keyschema': {
                    'type': 'string'
                }
            },
            'exclude': {
                'type': 'list',
                'items': {'type': 'string'},
                'default': []
            },
            'fsroot': {
                'type': 'string',
                'default': '/'
            }
        }
    }

    def __init__(self):

        self._targets = {}
        self._logger = logging.getLogger(__name__)

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

        # Do validation
        self._validate_configuration(config)

        # Create targets
        for key, settings in config['targets']:
            self._targets[key] = RaxolotlTarget(key,
                                                settings,
                                                config['defaults'])

    def _validate_configuration(self, config):
        """ Use cerberus to validate overall configuration """

        validator = cerberus.Validator(self._SCHEMA, )

        if not validator.validate(config):
            raise ConfigurationError("Configuration failed schema validation")


    @property
    def targets(self):
        """ Dictionary of RaxolotlTarget objects """
        return self._targets


class RaxolotlTarget(object):
    """ Target Configuration """

    def __init__(self, name, settings, defaults):

        self._logger = logging.getLogger(__name__)

        self._name = name
        self._settings = settings
        self._defaults = defaults

        self._validate_schema()

    def _generate_schema(self):
        """ Fill in the default values """

        schema = {
            'datastore': {
                'type': 'string',
                'empty': False
            },
            'hostname': {
                'type': 'string',
                'empty': False,
                'required': True
            },
            'exclude': {
                'type': 'list',
                'default': []
            },
            'snapshots': {
                'type': 'integer',
                'default': self._defaults['snapshots']
            },
            'retries': {
                'type': 'integer',
                'default': self._defaults['retries']
            },
            'fsroot': {
                'type': 'string',
                'default': self._defaults['fsroot']
            }
        }

        return schema

    def _validate_schema(self):
        """ Make sure our target is sane """

        # Get a schema with the defaults baked in
        schema = self._generate_schema()

        validator = cerberus.Validator(schema)


        if not validator.validate(self._settings):
            message = ("Target '{}' failed schema validation: {}"
                      ).format(self._name, validator.errors)
            self._logger.error(message)
            raise ConfigurationError(message)

        # Use normalize to apply defaults, etc
        self._settings = validator.normalized(self._settings)
        self._logger.debug("Target '%s' has been normalized to: %s",
                           self._name,
                           self._settings)

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
        exclude = self._defaults['exclude'][:]
        exclude.extend(self._settings['exclude'])

        return list(set(exclude))

    @property
    def retries(self):
        """ Number of times to retry """

        return self._settings['retries']
