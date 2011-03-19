# -*- coding: utf-8 -*-
import os
import sys

import logging
from django.utils import simplejson
sys.path.insert(0, './distlib.zip')
sys.path.insert(0, './lib')

from utils import setup_noderenderers
from utils import base64_decode

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from utils import setup_noderenderers
from utils import base64_decode

from google.appengine.ext.webapp.util import run_wsgi_app
import werkzeug
from flask import Flask, redirect, request, render_template


app = Flask(__name__)
app.debug = True


@app.route('/')
def blockdiag_index():
    kwargs = {}

    source = request.args.get('src')
    if source:
        kwargs['diagram'] = base64_decode(source)

    body = render_template('index.html', **kwargs)
    response = app.make_response(body)
    response.headers['Content-Type'] = 'application/xhtml+xml'
    return response


@app.route('/image', methods=['GET', 'POST'])
@app.route('/upload/image', methods=['GET', 'POST'])
def blockdiag_image():
    if request.method == 'POST':
        source = request.form['src']
    else:
        source = request.args.get('src')
    encoding = request.args.get('encoding')

    if encoding == 'base64':
        source = base64_decode(source)

    svg = blockdiag_generate_image(source)
    if encoding == 'jsonp':
        callback = request.args.get('callback')
        if callback and svg:
            json = simplejson.dumps({'image': svg}, ensure_ascii=False)
            jsonp = u'%s(%s)' % (callback, json)
        else:
            jsonp = ''

        response = app.make_response(jsonp)
        response.headers['Content-Type'] = 'text/javascript'
    else:
        response = app.make_response(svg)
        if encoding == 'base64':
            response.headers['Content-Type'] = 'image/svg+xml'
        else:
            response.headers['Content-Type'] = 'text/plain'

    return response


def blockdiag_generate_image(source):
    import blockdiag
    from blockdiag import diagparser
    from blockdiag.elements import DiagramNode, DiagramEdge

    try:
        DiagramNode.clear()
        DiagramEdge.clear()

        tree = diagparser.parse(diagparser.tokenize(source))
        diagram = blockdiag.blockdiag.ScreenNodeBuilder.build(tree)
        draw = blockdiag.DiagramDraw.DiagramDraw('SVG', diagram)
        draw.draw()
        svg = draw.save('')
    except Exception, e:
        svg = ''

    return svg.decode('utf-8')


@app.route('/seqdiag/')
def seqdiag_index():
    kwargs = {}

    source = request.args.get('src')
    if source:
        kwargs['diagram'] = base64_decode(source)

    body = render_template('seqdiag.html', **kwargs)
    response = app.make_response(body)
    response.headers['Content-Type'] = 'application/xhtml+xml'
    return response


@app.route('/seqdiag/image', methods=['GET', 'POST'])
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

        response = app.make_response(jsonp)
        response.headers['Content-Type'] = 'text/javascript'
    else:
        response = app.make_response(svg)
        if encoding == 'base64':
            response.headers['Content-Type'] = 'image/svg+xml'
        else:
            response.headers['Content-Type'] = 'text/plain'

    return response


def seqdiag_generate_image(source):
    import seqdiag
    from blockdiag.elements import DiagramNode, DiagramEdge

    try:
        DiagramNode.clear()
        DiagramEdge.clear()

        tree = seqdiag.diagparser.parse(seqdiag.diagparser.tokenize(source))
        diagram = seqdiag.seqdiag.DiagramTreeBuilder().build(tree)
        draw = seqdiag.seqdiag.DiagramDraw('SVG', diagram)
        draw.draw()
        svg = draw.save('')
    except Exception, e:
        self.errors = e
        svg = ''

    return svg.decode('utf-8')


@app.route('/upload/', methods=['GET', 'POST'])
def blockdiag_upload_form():
    import models
    pict_id = request.args.get('pict_id')

    if request.method == 'POST':
        file = request.files['img']
        diagram = blockdiag_generate_image_from_uploads(file)

        pict = models.Picture(diagram=diagram)
        pict.put()
        url = "/upload/?pict_id=%s" % pict.key()
        return redirect(url)
    elif request.method == 'GET' and pict_id is None:
        return render_template('upload.html')
    else:
        pict = models.Picture.get(pict_id)
        if pict is None:
            return redirect('/upload')

        diagram = pict.diagram

        body = render_template('upload2.html', diagram=diagram)
        response = app.make_response(body)
        response.headers['Content-Type'] = 'application/xhtml+xml'
        return response


@app.route('/tasks/delete_uploads')
def tasks_delete_uploads():
    import models
    from datetime import date, timedelta
    expire_date = date.today() - timedelta(7)

    query = models.Picture.all().filter('created_at <=', expire_date)
    for pict in query.fetch(1000):
         pict.delete()

    return ""


def blockdiag_generate_image_from_uploads(file):
    import png
    from itertools import izip

    pict = png.Reader(file=file)
    x, y, pixels, meta = pict.asRGBA8()

    diagram = """diagram{
       node_width=20;
       node_height=20;
       span_width=1;
       span_height=1;
    """

    for i, line in enumerate(pixels):
        if i > 32:
            continue

        nodes = []
        colors = (line[i:i + 4] for i in range(0, len(line), 4))
        for j, pixel in enumerate(colors):
            if j > 32:
                continue

            node = "%02d%02d" % (i, j)
            nodes.append(node)

            if pixel[3] == 0:
                rgb = [255, 255, 255]
            elif pixel[3] == 255:
                rgb = pixel[0:3]
            else:
                alpha = pixel[3] / 256.0
                bgcolor = 255 * (1 - alpha)
                rgb = [int(bgcolor + pixel[0] * alpha),
                       int(bgcolor + pixel[1] * alpha),
                           int(bgcolor + pixel[2] * alpha)]

            if rgb == [255, 255, 255]:
                diagram += '  %s [label=""];\n' % node
            else:
                diagram += '  %s [label="",color="#%02x%02x%02x"];\n' % \
                           (node, rgb[0], rgb[1], rgb[2])

        diagram += "  " + " -- ".join(nodes) + "\n"

    diagram += "}\n"

    return diagram


if __name__ == '__main__':
    setup_noderenderers()
    run_wsgi_app(app)
