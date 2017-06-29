# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from configuration import ConfigurationItem, EnvironmentConfigurationBackend, JsonFileConfigurationBackend

TOKEN = ConfigurationItem({
    'type': 'string',
    'empty': False,
    'default': 'Asdf'
})

BACKENDS = [
    EnvironmentConfigurationBackend(),
    JsonFileConfigurationBackend(file='config.json', location=JsonFileConfigurationBackend.CODE_ROOT_DIR),
    JsonFileConfigurationBackend(file='config.json', location=JsonFileConfigurationBackend.WORKING_DIR),
]
