import os
import sys
sys.path.insert(0, './distlib.zip')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class MainPage(webapp.RequestHandler):
    def get(self):
        fpath = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        params = {}
        html = template.render(fpath, params)

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(html)


application = webapp.WSGIApplication([('/', MainPage)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
