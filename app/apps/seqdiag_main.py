# -*- coding: utf-8 -*-
from utils import base64_decode
from flask import Module, redirect, request, make_response, render_template
from django.utils import simplejson

app = Module(__name__)


@app.route('/')
def seqdiag_index():
    kwargs = {}

    source = request.args.get('src')
    if source:
        kwargs['diagram'] = base64_decode(source)

    body = render_template('seqdiag.html', **kwargs)
    response = make_response(body)
    response.headers['Content-Type'] = 'application/xhtml+xml'
    return response


@app.route('/image', methods=['GET', 'POST'])
def seqdiag_image():
    if request.method == 'POST':
        source = request.form['src']
    else:
        source = request.args.get('src')
    encoding = request.args.get('encoding')

    if encoding == 'base64':
        source = base64_decode(source)

    svg = seqdiag_generate_image(source)
    if encoding == 'jsonp':
        callback = request.args.get('callback')
        if callback and svg:
            json = simplejson.dumps({'image': svg}, ensure_ascii=False)
            jsonp = u'%s(%s)' % (callback, json)
        else:
            jsonp = ''

        response = make_response(jsonp)
        response.headers['Content-Type'] = 'text/javascript'
    else:
        response = make_response(svg)
        if encoding == 'base64':
            response.headers['Content-Type'] = 'image/svg+xml'
        else:
            response.headers['Content-Type'] = 'text/plain'

    return response


def seqdiag_generate_image(source):
    import seqdiag
    from blockdiag.elements import DiagramNode, DiagramEdge, NodeGroup

    try:
        DiagramNode.clear()
        DiagramEdge.clear()
        NodeGroup.clear()

        tree = seqdiag.diagparser.parse(seqdiag.diagparser.tokenize(source))
        diagram = seqdiag.seqdiag.DiagramTreeBuilder().build(tree)
        draw = seqdiag.seqdiag.DiagramDraw('SVG', diagram)
        draw.draw()
        svg = draw.save('')
    except RuntimeError, e:
        svg = ''

    return svg.decode('utf-8')