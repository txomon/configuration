# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
"""Magical configuration loader/saver

.. moduleauthor:: Javier Domingo Cansino <javierdo1@gmail.com>
   :platform: Unix, Windows
   :synopsis: Magical configuration loaders/saver

Loading configuration is always horrible. The aim of this library is to follow after Netflix's Archaius to provide
configuration to your applications. It makes use of a little black magic to inject itself, but overall is a good boy.
"""

import _imp
import importlib.machinery
import json
import os
import sys
import types


class Validator:
    """Validating class, it's an optional dependency, so it's a placeholder
    """
    def __init__(self, *a, **kw):
        pass


class Configuration(types.ModuleType):
    """Configuration ModuleType. It makes sure to inject the descriptors
    
    """
    def __getattribute__(self, item):
        instance_value = object.__getattribute__(self, item)
        if hasattr(instance_value, '__get__'):
            value = instance_value.__get__(self, self.__class__)
            if hasattr(self.__class__, item):
                return value
            delattr(self, item)
            setattr(self.__class__, item, instance_value)
            instance_value.__set_name__(self, item)
            return value
        return instance_value


NoValue = object()


class ConfigurationBackend:
    is_dynamic = True
    """Marks if the backend can be modified externally (not from the configuration API). This affects caching."""
    is_writable = False
    """Marks if the backend accepts modifications through the configuration API (depends on the instance)"""

    def __init__(self, *args, write=False, dynamic=True, **kwargs):
        self.name = None
        self._value = NoValue
        self.instance = None

        if self.is_writable:
            self.is_writable = write
        elif write:
            raise ValueError(f'{self.__class__.__name__} is not a writable backend')

        if self.is_dynamic:
            self.is_dynamic = dynamic
        elif dynamic:
            raise ValueError(f'{self.__class__.__name__} is not a dynamic backend')

        self.initialize_backend(*args, **kwargs)

    def initialize_backend(self, *args, **kwargs):
        return

    def set_instance(self, instance):
        self.instance = instance

    def set_name(self, name):
        self.name = name

    def get_value(self):
        if not self.is_dynamic and self._value:
            return self._value
        self._value = value = self.get_real_value()
        return value

    def set_value(self, value):
        if not self.is_writable:
            raise AttributeError(f'{self.__class__.__name__} for item {self.name} is not writable')
        self.set_real_value(value)
        self._value = value

    def get_real_value(self):
        raise NotImplementedError(f'{self.__class__.__name__} is not implemented correctly')

    def set_real_value(self, value):
        raise AttributeError(f'{self.__class__.__name__} for item {self.name} is not writable')


class EnvironmentConfigurationBackend(ConfigurationBackend):
    def get_real_value(self):
        return os.environ.get(self.name.upper(), NoValue)


class JsonFileConfigurationBackend(ConfigurationBackend):
    CODE_ROOT_DIR = 1
    WORKING_DIR = 2

    def initialize_backend(self, file, location, compulsory=False):
        self.file = file
        self.location = location
        self.compulsory = compulsory
        self.file_location = None

    def _get_location(self):
        if self.location == self.CODE_ROOT_DIR:
            module_name, file_name = self.instance.__name__, self.instance.__file__
            module_path = module_name.replace('.', os.path.sep)
            code_root_directory = file_name.rsplit(module_path, 1)[0]
            return code_root_directory
        if self.location == self.WORKING_DIR:
            return os.getcwd()
        return self.location

    def get_file_location(self):
        if self.file_location:
            return self.file_location
        location = self._get_location()
        self.file_location = os.path.join(location, self.file)
        return self.file_location

    def get_real_value(self):
        if not os.path.exists(self.get_file_location()):
            if self.compulsory:
                raise FileNotFoundError(
                    f'File {self.file_location} is compulsory but cannot be found for {self.__class__.__name__}')
            else:
                return NoValue
        with open(self.file_location) as fd:
            return json.loads(fd.read()).get(self.name.lower(), NoValue)


class ConfigurationItem:
    def __init__(self, *spec, backends=None, **schema):
        self.backends = backends
        self.name = None
        self.validator = None
        if schema:
            assert len(schema) == 1
            self.__set_name__(None, schema.keys()[0])
            self.spec = schema[self.name]
            self.validator = Validator(schema)
        elif spec:
            assert len(spec) == 1
            self.spec = spec[0]
        else:
            assert any([spec, schema])

    def _init_schema(self, instance=None):
        if self.name and self.validator and self.backends:
            return
        if not instance:
            raise ValueError('Argument instance was not passed while still not initialized')
        if not self.backends:
            assert hasattr(instance, 'BACKENDS'), 'No default configuration.BACKENDS and no explicit backends set'
            self.backends = instance.BACKENDS
        for backend in self.backends:
            backend.set_instance(instance)
        for var_name, value in vars(instance).items():
            if value == self:
                self.__set_name__(None, var_name)
                self.validator = Validator({self.name: self.spec})
                return
        raise AttributeError('Object does not contain descriptor')

    def __get__(self, instance, owner):
        self._init_schema(instance)
        values = [backend.get_value() for backend in self.backends]
        value = self.spec.get('default', NoValue)
        for backend_value in values:
            if backend_value is not NoValue:
                value = backend_value
        if value is NoValue:
            raise ValueError(f'{self.name} is not defined in any backend, and has no default value')
        return value

    def __set_name__(self, owner, name):
        if self.name and self.name != name:
            raise AttributeError(f'Trying to change the name of the ConfigurationItem from {self.name} to {name}')
        self.name = name
        for backend in self.backends:
            backend.set_name(name=name)

    def __set__(self, instance, value):
        writable_backends = [backend for backend in self.backends if backend.is_writable]
        if not writable_backends:
            raise AttributeError(f"ConfigurationItem {self.name} doesn't have any writable backend")
        for backend in writable_backends:
            backend.set_value(value)

    def set(self, value):
        self.__set__(None, value)


# This is extracted from the logic at importlib._bootstrap_external.py::_get_supported_file_loaders
class ConfigurationExtensionFileLoader(importlib.machinery.ExtensionFileLoader):
    def create_module(self, spec):
        if not spec.name.endswith('configuration'):
            return None
        return type(spec.name, (Configuration,), {})(spec.name)


class ConfigurationSourceFileLoader(importlib.machinery.SourceFileLoader):
    def create_module(self, spec):
        if not spec.name.endswith('configuration'):
            return None
        return type(spec.name, (Configuration,), {})(spec.name)


class ConfigurationSourcelessFileLoader(importlib.machinery.SourcelessFileLoader):
    def create_module(self, spec):
        if not spec.name.endswith('configuration'):
            return None
        return type(spec.name, (Configuration,), {})(spec.name)


sys.path_hooks.insert(0, importlib.machinery.FileFinder.path_hook(
    (ConfigurationExtensionFileLoader, _imp.extension_suffixes()),
    (ConfigurationSourceFileLoader, importlib.machinery.SOURCE_SUFFIXES),
    (ConfigurationSourcelessFileLoader, importlib.machinery.BYTECODE_SUFFIXES),
))
