# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from app import configuration


# Default de 5
def main():

    global TOKEN
    print(app.configuration.TOKEN)  # 5
    print(TOKEN)  # 5
    # app.configuration.TOKEN = 9
    print(app.configuration.TOKEN)  # 9
    print(TOKEN)  # 5
    # TOKEN = 7
    print(app.configuration.TOKEN)  # 9
    print(TOKEN)  # 7
    print(app.configuration.JAVIER)  # DOMINGO
    print(app.configuration.JON)  # vacio, ander

if __name__ == '__main__':
    main()
