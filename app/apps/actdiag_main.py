# -*- coding: utf-8 -*-
from utils import base64_decode
from flask import Module, redirect, request, make_response, render_template
from django.utils import simplejson

app = Module(__name__)


@app.route('/')
def actdiag_index():
    kwargs = {}

    source = request.args.get('src')
    if source:
        kwargs['diagram'] = base64_decode(source)

    body = render_template('actdiag.html', **kwargs)
    response = make_response(body)
    response.headers['Content-Type'] = 'application/xhtml+xml'
    return response


@app.route('/image', methods=['GET', 'POST'])
def actdiag_image():
    if request.method == 'POST':
        source = request.form['src']
    else:
        source = request.args.get('src')
    encoding = request.args.get('encoding')

    if encoding == 'base64':
        source = base64_decode(source)

    svg = actdiag_generate_image(source)
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


def actdiag_generate_image(source):
    import actdiag
    from blockdiag import diagparser
    from actdiag.elements import DiagramNode, DiagramEdge, NodeGroup

    try:
        DiagramNode.clear()
        DiagramEdge.clear()
        NodeGroup.clear()

        tree = diagparser.parse(diagparser.tokenize(source))
        diagram = actdiag.actdiag.ScreenNodeBuilder.build(tree)
        draw = actdiag.DiagramDraw.DiagramDraw('SVG', diagram)
        draw.draw()
        svg = draw.save('')
    except Exception, e:
        svg = ''

    return svg.decode('utf-8')