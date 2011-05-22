# -*- coding: utf-8 -*-
from lib.utils import base64_decode, get_redirector, json as simplejson
from flask import Module, redirect, request, make_response, render_template

app = Module(__name__)


@app.route('/')
def graphviz_index():
    kwargs = {}

    redirector = get_redirector('graphviz', request)
    if redirector:
        return redirector

    source = request.args.get('src')
    if source:
        kwargs['diagram'] = base64_decode(source)

    body = render_template('graphviz.html', **kwargs)
    response = make_response(body)
    response.headers['Content-Type'] = 'application/xhtml+xml'
    return response
