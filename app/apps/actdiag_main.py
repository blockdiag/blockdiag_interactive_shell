# -*- coding: utf-8 -*-
from lib.utils import base64_decode, json as simplejson
from flask import Module, redirect, request, make_response, render_template

app = Module(__name__)


@app.route('/')
def actdiag_index():
    import actdiag
    kwargs = {'version': actdiag.__version__}

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
    from actdiag import diagparser, builder, DiagramDraw

    try:
        tree = diagparser.parse(diagparser.tokenize(source))
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = DiagramDraw.DiagramDraw('SVG', diagram)
        draw.draw()
        svg = draw.save('')
    except Exception, e:
        svg = ''

    return svg.decode('utf-8')
