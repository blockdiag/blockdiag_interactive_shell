import os
import sys
from django.utils import simplejson
sys.path.insert(0, './distlib.zip')
sys.path.insert(0, './lib')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from blockdiag.blockdiag import *
from blockdiag.diagparser import *


class MainPage(webapp.RequestHandler):
    def get(self):
        fpath = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        params = {}
        html = template.render(fpath, params)

        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.out.write(html)


class ImagePage(webapp.RequestHandler):
    def get(self):
        callback = self.request.get('callback')
        source = self.request.get('src')

        svg = self.generate_image(source)
        if callback and svg:
            json = simplejson.dumps({'image': svg}, ensure_ascii=False)
            jsonp = '%s(%s)' % (callback, json)
        else:
            jsonp = ''

        self.response.headers['Content-Type'] = 'text/javascript'
        self.response.out.write(jsonp)

    def post(self):
        source = self.request.get('src')
        svg = self.generate_image(source)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(svg)

    def generate_image(self, source):
        try:
            tree = parse(tokenize(source))
            diagram = ScreenNodeBuilder.build(tree)
            draw = DiagramDraw.DiagramDraw('SVG', diagram)
            draw.draw()
            svg = draw.save('')
        except:
            svg = ''

        return svg


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/image', ImagePage)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
