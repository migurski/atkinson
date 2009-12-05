# totally swiped from http://www.python.org/doc/2.5.2/ext/building.html
from distutils.core import setup, Extension

atk = Extension('atk', sources = ['atk.c'])

setup (name = 'atk',
       version = '1.0',
       description = 'Stub function which takes a string and returns a string',
       ext_modules = [atk])
