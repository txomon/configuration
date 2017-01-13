# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import _imp
import importlib.machinery
import sys
import types
from collections import defaultdict


class Validator:
    def __init__(self, *a, **kw):
        pass


class Configuration(types.ModuleType):
    _modules = defaultdict(set)

    def __getattribute__(self, item):
        instance_value = object.__getattribute__(self, item)
        if hasattr(instance_value, '__get__'):
            delattr(self, item)
            setattr(self.__class__, item, instance_value)
            return instance_value.__get__(self, self.__class__)
        return instance_value


class ConfigurationItem:
    def __init__(self, *spec, **schema):
        self._value = 5
        if schema:
            assert len(schema) == 1
            self.name = schema.keys()[0]
            self.spec = schema[self.name]
            self.validator = Validator(schema)
        elif spec:
            assert len(spec) == 1
            self.name = None
            self.spec = spec[0]
            self.validator = None
        else:
            assert any([spec, schema])

    def _init_schema(self, instance=None):
        if self.name and self.validator:
            return
        for var_name, value in vars(instance).items():
            if value == self:
                self.name = var_name
                self.validator = Validator({self.name: self.spec})
                return var_name
        assert False, 'Object does not contain descriptor'

    def __get__(self, instance, owner):
        return self._value
        self._init_schema(instance)

    def __set_name__(self, owner, name):
        pass

    def __set__(self, instance, value):
        self._value = value

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
