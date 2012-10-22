# -*- coding: utf-8 -*-
import re
import os
import sys
import base64
import zlib
import blockdiag
import blockdiag.noderenderer
import blockdiagcontrib
import actdiag.plugins
import blockdiag.plugins

if sys.version_info >= (2, 6):
    import json as simplejson
else:
    try:
        from django.utils import simplejson
    except ImportError:
        import simplejson


# for supporting base64.js
def base64_decode(string):
    string = re.sub('-', '+', string)
    string = re.sub('_', '/', string)

    padding = len(string) % 4
    if padding > 0:
        string += "=" * (4 - padding)

    return base64.b64decode(string)

def decode_source(source, encoding, compression):
    if encoding == 'base64':
        source = base64_decode(source)

    if compression == 'deflate':
        source = zlib.decompress(source)

    if isinstance(source, str):
        source = unicode(source, 'UTF-8')

    return source

def get_hostname():
    if os.environ.get('HTTP_HOST'):
        hostname = os.environ['HTTP_HOST']
    elif os.environ.get('SERVER_NAME'):
        hostname = os.environ['SERVER_NAME']
    else:
        hostname = None

    return hostname


def get_redirect_url(urlbase, request):
    url = None
    if 'HTTP_HOST' not in os.environ:
        return None

    if os.environ['HTTP_HOST'] == 'blockdiag.appspot.com':
        url = 'http://interactive.blockdiag.com/'

    if os.environ['HTTP_HOST'] == 'blockdiag-dev.appspot.com':
        url = 'http://dev.interactive.blockdiag.com/'

    if url:
        if urlbase:
            url += "%s/" % urlbase

        if request.args.get('src'):
            url += '?src=%s' % request.args.get('src')
        if request.args.get('compression'):
            url += '&compression=%s' % request.args.get('compression')

    return url


def setup_plugins():
    blockdiag.plugins.node_handlers = []

    import pkg_resources
    modules = ('attributes', 'autoclass',)
    for name in modules:
        _name = 'blockdiag.plugins.' + name
        __import__(_name, fromlist=blockdiag.plugins)
        m = sys.modules[_name]

        pkg_resources.plugins[name] = m

    modules = ('autolane',)
    for name in modules:
        _name = 'actdiag.plugins.' + name
        __import__(_name, fromlist=actdiag.plugins)
        m = sys.modules[_name]

        pkg_resources.plugins[name] = m


def get_fontmap():
    from StringIO import StringIO
    from blockdiag.utils.fontmap import FontMap
    from blockdiag.utils.collections import namedtuple

    dummy = re.sub('pyc', 'py', __file__)

    config = open(u"%s/../fontmaprc" % os.path.dirname(dummy)).read()
    config = re.sub('FILENAME', dummy, config)
    options = namedtuple('Option', 'font fontmap')(None, StringIO(config))
    fmap = FontMap(StringIO(config))
    return fmap


def setup_noderenderers():
    modules = ('box', 'square', 'roundedbox', 'diamond', 'minidiamond',
               'mail', 'textbox', 'none', 'note', 'cloud',
               'circle', 'ellipse', 'beginpoint', 'endpoint', 'dots', 'actor',
               'flowchart.database', 'flowchart.input',
               'flowchart.loopin', 'flowchart.loopout', 'flowchart.terminator')
    for name in modules:
        name = 'blockdiag.noderenderer.' + name
        __import__(name, fromlist=blockdiag.noderenderer)
        m = sys.modules[name]

        m.setup(m)

    import packetdiag.noderenderers
    packetdiag.noderenderers.setup(packetdiag.noderenderers)

    modules = ('class', 'labeled_box', 'qb')
    for name in modules:
        name = 'blockdiagcontrib.' + name
        __import__(name, fromlist=blockdiagcontrib)
        m = sys.modules[name]

        m.setup(m)

    import cisco
    cisco.setup(cisco, 'http://%s/static/cisco_images' % get_hostname())

    import nationalflags
    nationalflags.setup(nationalflags, 'http://%s/static/flag_images' % get_hostname())
