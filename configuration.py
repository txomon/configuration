# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import _imp
import importlib.machinery
import os
import sys
import types


class Validator:
    def __init__(self, *a, **kw):
        pass


class Configuration(types.ModuleType):
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
    is_dynamic = False
    is_writable = False

    def __init__(self, *args, write=False, dynamic=False, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self.name = None
        self._value = NoValue

        if self.is_writable:
            self.is_writable = write
        elif write:
            raise ValueError(f'{self.__class__.__name__} is not a writable backend')

        if self.is_dynamic:
            self.is_dynamic = dynamic
        elif dynamic:
            raise ValueError(f'{self.__class__.__name__} is not a dynamic backend')

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
        raise NotImplementedError()

    def set_real_value(self, value):
        raise AttributeError(f'{self.__class__.__name__} for item {self.name} is not writable')


class EnvironmentConfigurationBackend(ConfigurationBackend):
    is_dynamic = True

    def get_real_value(self):
        return os.environ.get(self.name.upper(), None)


class JsonFileConfigurationBackend(ConfigurationBackend):
    CODE_ROOT_DIR = 1
    WORKING_DIR = 2
    is_dynamic = True

    def get_real_value(self):
        raise NotImplementedError()


class ConfigurationItem:
    def __init__(self, *spec, backends=None, **schema):
        if not backends:
            backends = [
                EnvironmentConfigurationBackend(),
                JsonFileConfigurationBackend(file='config.json', location=JsonFileConfigurationBackend.CODE_ROOT_DIR),
                JsonFileConfigurationBackend(file='config.json', location=JsonFileConfigurationBackend.WORKING_DIR),
            ]
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
        if self.name and self.validator:
            return
        if not instance:
            raise ValueError('Argument instance was not passed while still not initialized')
        for var_name, value in vars(instance).items():
            if value == self:
                self.__set_name__(None, var_name)
                self.validator = Validator({self.name: self.spec})
                return
        raise AttributeError('Object does not contain descriptor')

    def __get__(self, instance, owner):
        self._init_schema(instance)

    def __set_name__(self, owner, name):
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
