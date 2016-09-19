""" Various Exceptions """

class ConfigurationError(Exception):
    """ Configuration error base """

class ConfigurationNotFound(ConfigurationError):
    """ When we can't find the file """

class ConfigurationParseError(ConfigurationError):
    """For when the YAML doens't parse or we are missing a required
    element """
