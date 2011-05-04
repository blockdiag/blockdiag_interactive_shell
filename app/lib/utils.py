# -*- coding: utf-8 -*-
import re
import sys
import base64
import blockdiag
import blockdiag.noderenderer
import blockdiagcontrib

if sys.version_info >= (2, 6):
    import json
else:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import simplejson as json


# for supporting base64.js
def base64_decode(string):
    string = re.sub('-', '+', string)
    string = re.sub('_', '/', string)

    padding = len(string) % 4
    if padding > 0:
        string += "=" * (4 - padding)

    return unicode(base64.b64decode(string), 'UTF-8')


def setup_noderenderers():
    modules = ('box', 'roundedbox', 'diamond', 'minidiamond', 'mail',
               'note', 'cloud', 'ellipse', 'beginpoint', 'endpoint',
               'actor', 'flowchart.database', 'flowchart.input',
               'flowchart.loopin', 'flowchart.loopout', 'flowchart.terminator')
    for name in modules:
        name = 'blockdiag.noderenderer.' + name
        __import__(name, fromlist=blockdiag.noderenderer)
        m = sys.modules[name]

        m.setup(m)

    modules = ('class', 'square', 'qb')
    for name in modules:
        name = 'blockdiagcontrib.' + name
        __import__(name, fromlist=blockdiagcontrib)
        m = sys.modules[name]

        m.setup(m)

    import renderers
    renderers.setup(renderers)
