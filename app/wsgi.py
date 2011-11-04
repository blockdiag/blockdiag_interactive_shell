import sys
sys.path.insert(0, './lib')
sys.path.insert(0, './distlib.zip')

from main import app
from utils import setup_noderenderers


def application(environ, start_response):
    return app(environ, start_response)
