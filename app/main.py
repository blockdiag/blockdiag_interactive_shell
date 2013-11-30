# -*- coding: utf-8 -*-
import os
import sys

# load fake_setuptools (at appengine env)
try:
    from google.appengine.ext.webapp.util import run_wsgi_app
    sys.path.insert(0, './lib/fake_setuptools')
except:
    pass

sys.path.insert(0, './distlib.zip')
sys.path.insert(0, './lib')

import werkzeug
from flask import Flask, redirect, request, render_template
from lib.utils import setup_imagedraw, setup_plugins, setup_noderenderers


app = Flask(__name__)
app.debug = True

import apps.blockdiag_main
app.register_blueprint(apps.blockdiag_main.app)
app.register_blueprint(apps.blockdiag_main.app, url_prefix='/blockdiag')

import apps.seqdiag_main
app.register_blueprint(apps.seqdiag_main.app, url_prefix='/seqdiag')

import apps.actdiag_main
app.register_blueprint(apps.actdiag_main.app, url_prefix='/actdiag')

import apps.nwdiag_main
app.register_blueprint(apps.nwdiag_main.app, url_prefix='/nwdiag')

import apps.rackdiag_main
app.register_blueprint(apps.rackdiag_main.app, url_prefix='/rackdiag')

import apps.packetdiag_main
app.register_blueprint(apps.packetdiag_main.app, url_prefix='/packetdiag')

import apps.graphviz_main
app.register_blueprint(apps.graphviz_main.app, url_prefix='/graphviz')


@app.route('/tasks/delete_uploads')
def tasks_delete_uploads():
    import models
    from datetime import date, timedelta
    expire_date = date.today() - timedelta(7)

    query = models.Picture.all().filter('created_at <=', expire_date)
    for pict in query.fetch(1000):
         pict.delete()

    return ""


def app_factory(global_config, **local_conf):
    """ wsgi app factory for Paste """
    setup_plugins()
    setup_noderenderers()
    return app


# initialize
setup_imagedraw()
setup_plugins()
setup_noderenderers()
