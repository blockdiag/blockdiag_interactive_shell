import os
import sys
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
    def post(self):
        try:
            tree = parse(tokenize(self.request.get('src')))
            diagram = ScreenNodeBuilder.build(tree)
            draw = DiagramDraw.DiagramDraw('SVG', diagram)
            draw.draw()
            svg = draw.save('')
        except:
            svg = ''

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(svg)


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/image', ImagePage)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
