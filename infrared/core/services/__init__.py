"""Service locator for the IR services

Stores and resolves all the dependencies for the services.
"""
import os

try:  # py2
    import ConfigParser
except ImportError:  # py3
    import configparser as ConfigParser

from infrared.core.services import profiles
from infrared.core.services import plugins
from infrared.core.utils import logger

LOG = logger.LOG


class ServiceName(object):
    """Holds the supported services names. """
    PROFILE_MANAGER = "profile_manager"
    PLUGINS_MANAGER = "plugins_manager"


class CoreServices(object):
    """Holds and configures all the required for core services. """

    _SERVICES = {}
    DEFAULTS = {
        'profiles_base_folder': '.profiles',
        'plugins_conf_file': '.plugins.ini'
    }

    @classmethod
    def init(cls, file_path='infrared.cfg', section='core'):
        """Creates configuration from file or from defaults. """

        config = ConfigParser.ConfigParser()
        # if file not found no exception will be raised
        config.read(file_path)
        cls.from_dict(
            dict(config.items(section))
            if config.has_section(section) else None)

    @classmethod
    def from_dict(cls, conf_dict=None):
        """Configures services using the dictionary of settings.

        Check the CoreServices.DEFAULTS for the dict structure.
        """
        if conf_dict is None:
            conf_dict = {}
        cls._configure(
            os.path.abspath(
                cls.__get_opiton(conf_dict, 'profiles_base_folder')),
            os.path.abspath(
                cls.__get_opiton(conf_dict, 'plugins_conf_file'))
        )

    @classmethod
    def __get_opiton(cls, conf, name):
        """Gets an option from a dict or returns a default option value. """
        return conf.get(name, cls.DEFAULTS[name])

    @classmethod
    def _configure(cls, profile_dir, plugins_conf):
        """Register services to manager. """

        # create profile manager
        if ServiceName.PROFILE_MANAGER not in CoreServices._SERVICES:
            cls.register_service(ServiceName.PROFILE_MANAGER,
                                 profiles.ProfileManager(profile_dir))
        # create plugins manager
        if ServiceName.PLUGINS_MANAGER not in CoreServices._SERVICES:
            cls.register_service(ServiceName.PLUGINS_MANAGER,
                                 plugins.InfraRedPluginManager(plugins_conf))

    @classmethod
    def register_service(cls, service_name, service):
        """Protect the _SERVICES dict"""
        CoreServices._SERVICES[service_name] = service

    @classmethod
    def _get_service(cls, name):
        if name not in cls._SERVICES:
            cls.from_dict()
        return cls._SERVICES[name]

    @classmethod
    def profile_manager(cls):
        """Gets the profile manager. """
        return cls._get_service(ServiceName.PROFILE_MANAGER)

    @classmethod
    def plugins_manager(cls):
        """Gets the plugin manager. """
        return cls._get_service(ServiceName.PLUGINS_MANAGER)
