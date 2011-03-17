# -*- coding: utf-8 -*-
import os
import sys

from utils import setup_noderenderers
from utils import base64_decode
import logging
from django.utils import simplejson
sys.path.insert(0, './distlib.zip')
sys.path.insert(0, './lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from utils import setup_noderenderers
from utils import base64_decode

from blockdiag.elements import *
import blockdiag
import seqdiag


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


class ImageUploadMainPage(webapp.RequestHandler):
    def get(self):
        dirname = os.path.dirname(__file__)
        fpath = os.path.join(dirname, 'templates', 'upload.html')
        html = template.render(fpath, {})

        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.out.write(html)

    def post(self):
        import png
        from StringIO import StringIO
        from itertools import izip

        io = StringIO(self.request.get('img'))
        pict = png.Reader(file=io)
        x, y, pixels, meta = pict.asRGB8()

        diagram = """diagram{
           node_width=20;
           node_height=20;
           span_width=1;
           span_height=1; 
        """

        for i, line in enumerate(pixels):
            if i > 32:
                continue

            it = iter(line)
            nodes = []
            for j, pixel in enumerate(izip(it, it, it)):
                if j > 32:
                    continue

                node = "x%dy%d" % (i, j)
                nodes.append(node)

                diagram += '  %s[label="",color="#%02x%02x%02x"];\n' % \
                           (node, pixel[0], pixel[1], pixel[2])

            diagram += "  " + " -- ".join(nodes) + "\n"

        diagram += "}\n"


        dirname = os.path.dirname(__file__)
        fpath = os.path.join(dirname, 'templates', 'upload2.html')
        html = template.render(fpath, {'diagram': diagram})

        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.out.write(html)


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/image', ImagePage),
                                      ('/seqdiag/', SeqdiagMainPage),
                                      ('/seqdiag/image', SeqdiagImagePage),
                                      ('/upload', ImageUploadMainPage)],
                                     debug=True)


def main():
    setup_noderenderers()
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
