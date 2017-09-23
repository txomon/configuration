# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from configuration import ConfigurationItem, EnvironmentConfigurationBackend, JsonFileConfigurationBackend, SQLiteConfigurationBackend

TOKEN = ConfigurationItem({
    'type': 'string',
    'empty': False,
    'default': 'Asdf'
})

JAVIER = ConfigurationItem({
    'type': 'string',
    'empty': False,
    'default': '1'
})

JON = ConfigurationItem({
    'type': 'string',
    'empty': False,
    'default': 'ander'
})

BACKENDS = [
    EnvironmentConfigurationBackend(),
    JsonFileConfigurationBackend(file='config.json', location=JsonFileConfigurationBackend.CODE_ROOT_DIR),
    SQLiteConfigurationBackend(file='db.sqlite', table='configuration', location=JsonFileConfigurationBackend.WORKING_DIR),
    JsonFileConfigurationBackend(file='config.json', location=JsonFileConfigurationBackend.WORKING_DIR)
]
