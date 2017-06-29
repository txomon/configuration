# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from setuptools import setup

setup(
    name='lince',
    version='0.0.1a',
    description='Configuration engine',
    long_description=open('README.rst').read(),
    url='https://github.com/txomon/lince',
    author='Javier Domingo Cansino',
    author_email='javierdo1@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    py_modules=['configuration'],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
    keywords=['configuration', 'config', 'dynamic', 'file', 'json', 'environment', 'variable'],

)
