# -*- coding: utf-8 -*-
from utils import base64_decode
from flask import Module, redirect, request, make_response, render_template
from django.utils import simplejson

app = Module(__name__)


@app.route('/')
def graphviz_index():
    kwargs = {}

    source = request.args.get('src')
    if source:
        kwargs['diagram'] = base64_decode(source)

    body = render_template('graphviz.html', **kwargs)
    response = make_response(body)
    response.headers['Content-Type'] = 'application/xhtml+xml'
    return response
