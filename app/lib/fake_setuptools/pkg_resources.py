# -*- coding: utf-8 -*-

from collections import namedtuple

plugins = {}


def fake_entry_point(module):
    EntryPoint = namedtuple('EntryPoint', 'load')
    return EntryPoint(lambda: module)


def declare_namespace(*args, **kwargs):
    pass


def iter_entry_points(*args, **kwargs):
    name = args[1]
    if name in plugins:
        ep = fake_entry_point(plugins[name])
        return [ep]
    else:
        return []
