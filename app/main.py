# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, './distlib.zip')

import werkzeug
from flask import Flask, redirect, request, render_template
from lib.utils import setup_noderenderers


app = Flask(__name__)
app.debug = True

import apps.blockdiag_main
app.register_module(apps.blockdiag_main.app)

import apps.seqdiag_main
app.register_module(apps.seqdiag_main.app, url_prefix='/seqdiag')

import apps.actdiag_main
app.register_module(apps.actdiag_main.app, url_prefix='/actdiag')

import apps.netdiag_main
app.register_module(apps.netdiag_main.app, url_prefix='/netdiag')

import apps.graphviz_main
app.register_module(apps.graphviz_main.app, url_prefix='/graphviz')


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
    setup_noderenderers()
    return app


if __name__ == '__main__':
    from google.appengine.ext.webapp.util import run_wsgi_app
    setup_noderenderers()
    run_wsgi_app(app)
