# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from app import configuration


# Default de 5
def main():
    print(configuration.TOKEN)  # 5
    configuration.TOKEN = 9
    print(configuration.TOKEN)  # 9


if __name__ == '__main__':
    main()
