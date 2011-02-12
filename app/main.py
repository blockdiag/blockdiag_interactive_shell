import os
import sys
import re
import base64
import logging
from django.utils import simplejson
sys.path.insert(0, './distlib.zip')
sys.path.insert(0, './lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from blockdiag.elements import *
import blockdiag
import seqdiag


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


class MainPage(webapp.RequestHandler):
    def get(self):
        dirname = os.path.dirname(__file__)
        fpath = os.path.join(dirname, 'templates', 'index.html')
        params = {}

        source = self.request.get('src')
        if source:
            params['diagram'] = base64_decode(source)

        html = template.render(fpath, params)

        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.out.write(html)


class ImagePage(webapp.RequestHandler):
    def get(self):
        callback = self.request.get('callback')
        source = self.request.get('src')
        encoding = self.request.get('encoding', 'jsonp')

        if encoding == 'base64':
            source = base64_decode(source)

        svg = self.generate_image(source)
        if encoding == 'jsonp':
            if callback and svg:
                json = simplejson.dumps({'image': svg}, ensure_ascii=False)
                jsonp = u'%s(%s)' % (callback, json)
            else:
                jsonp = ''

            self.response.headers['Content-Type'] = 'text/javascript'
            self.response.out.write(jsonp)
        elif encoding == 'base64':
            self.response.headers['Content-Type'] = 'image/svg+xml'
            self.response.out.write(svg)

    def post(self):
        source = self.request.get('src')
        svg = self.generate_image(source)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(svg)

    def generate_image(self, source):
        try:
            DiagramNode.clear()
            DiagramEdge.clear()

            tree = blockdiag.diagparser.parse(blockdiag.diagparser.tokenize(source))
            diagram = blockdiag.blockdiag.ScreenNodeBuilder.build(tree)
            draw = blockdiag.DiagramDraw.DiagramDraw('SVG', diagram)
            draw.draw()
            svg = draw.save('')
        except Exception, e:
            self.errors = e
            svg = ''

        return svg.decode('utf-8')


class SeqdiagMainPage(webapp.RequestHandler):
    def get(self):
        dirname = os.path.dirname(__file__)
        fpath = os.path.join(dirname, 'templates', 'seqdiag.html')
        params = {}

        source = self.request.get('src')
        if source:
            params['diagram'] = base64_decode(source)

        html = template.render(fpath, params)

        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.out.write(html)


class SeqdiagImagePage(webapp.RequestHandler):
    def get(self):
        callback = self.request.get('callback')
        source = self.request.get('src')
        encoding = self.request.get('encoding', 'jsonp')

        if encoding == 'base64':
            source = base64_decode(source)

        svg = self.generate_image(source)
        if encoding == 'jsonp':
            if callback and svg:
                json = simplejson.dumps({'image': svg}, ensure_ascii=False)
                jsonp = u'%s(%s)' % (callback, json)
            else:
                jsonp = ''

            self.response.headers['Content-Type'] = 'text/javascript'
            self.response.out.write(jsonp)
        elif encoding == 'base64':
            self.response.headers['Content-Type'] = 'image/svg+xml'
            self.response.out.write(svg)

    def post(self):
        source = self.request.get('src')
        svg = self.generate_image(source)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(svg)

    def generate_image(self, source):
        try:
            DiagramNode.clear()
            DiagramEdge.clear()

            tree = seqdiag.diagparser.parse(seqdiag.diagparser.tokenize(source))
            diagram = seqdiag.seqdiag.DiagramTreeBuilder().build(tree)
            draw = seqdiag.seqdiag.DiagramDraw('SVG', diagram)
            draw.draw()
            svg = draw.save('')
        except Exception, e:
            self.errors = e
            svg = ''

        return svg.decode('utf-8')


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/image', ImagePage),
                                      ('/seqdiag/', SeqdiagMainPage),
                                      ('/seqdiag/image', SeqdiagImagePage)], debug=True)


def main():
    setup_noderenderers()
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
