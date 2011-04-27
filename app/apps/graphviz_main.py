# -*- coding: utf-8 -*-
from lib.utils import base64_decode, json
from flask import Module, redirect, request, make_response, render_template

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
