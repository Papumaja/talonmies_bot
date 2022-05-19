"""The all the commands in submodules starting with 'cmd_' can be imported
straight from this module
(from commands import cmd_start, from commands import *)
"""
import pkgutil
from importlib import import_module

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    module = import_module(f'{__name__}.{module_name}')
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if attribute_name[:4] == 'cmd_':
            globals()[attribute_name] = attribute