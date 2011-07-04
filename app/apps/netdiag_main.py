# -*- coding: utf-8 -*-
from lib.utils import base64_decode, simplejson
from flask import Blueprint, redirect, request, make_response, render_template

app = Blueprint('netdiag_main', __name__)


@app.route('/')
def netdiag_index():
    url = '/nwdiag'

    source = request.args.get('src')
    if source:
        url += "/?src=%s" % source

    return redirect(url)


@app.route('/image', methods=['GET', 'POST'])
def netdiag_image():
    if request.method == 'POST':
        source = request.form['src']
    else:
        source = request.args.get('src')
    encoding = request.args.get('encoding')

    if encoding == 'base64':
        source = base64_decode(source)

    svg = netdiag_generate_image(source)
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


def netdiag_generate_image(source):
    import netdiag
    from netdiag import diagparser, builder, DiagramDraw

    try:
        tree = diagparser.parse_string(source)
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = DiagramDraw.DiagramDraw('SVG', diagram)
        draw.draw()
        svg = draw.save('')
    except Exception, e:
        svg = ''

    return svg.decode('utf-8')
