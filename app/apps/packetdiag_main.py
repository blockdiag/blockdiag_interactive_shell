# -*- coding: utf-8 -*-
from lib.utils import decode_source, get_redirect_url, get_fontmap, simplejson
from flask import Blueprint, redirect, request, make_response, render_template

app = Blueprint('packetdiag_main', __name__)


@app.route('/')
def packetdiag_index():
    import packetdiag
    kwargs = {'version': packetdiag.__version__}

    url = get_redirect_url('packetdiag', request)
    if url:
        return redirect(url)

    source = request.args.get('src')
    if source:
        compression = request.args.get('compression')
        kwargs['diagram'] = decode_source(source, 'base64', compression)

    body = render_template('packetdiag.html', **kwargs)
    response = make_response(body)
    response.headers['Content-Type'] = 'application/xhtml+xml'
    return response


@app.route('/image', methods=['GET', 'POST'])
def packetdiag_image():
    if request.method == 'POST':
        source = request.form['src']
    else:
        source = request.args.get('src')

    encoding = request.args.get('encoding')
    compression = request.args.get('compression')

    source = decode_source(source, encoding, compression)

    format = request.args.get('format', 'SVG')
    image = packetdiag_generate_image(source, format)
    if encoding == 'jsonp':
        callback = request.args.get('callback')
        if callback:
            json = simplejson.dumps(image, ensure_ascii=False)
            jsonp = u'%s(%s)' % (callback, json)
        else:
            jsonp = ''

        response = make_response(jsonp)
        response.headers['Content-Type'] = 'text/javascript'
    else:
        response = make_response(image['image'])
        if format == 'PNG':
            response.headers['Content-Type'] = 'image/png'
        elif encoding == 'base64':
            response.headers['Content-Type'] = 'image/svg+xml'
        else:
            response.headers['Content-Type'] = 'text/plain'

    return response


def packetdiag_generate_image(source, format):
    import packetdiag
    from packetdiag import parser, builder, drawer

    try:
        tree = parser.parse_string(source)
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = drawer.DiagramDraw(format, diagram, fontmap=get_fontmap())
        draw.draw()

        image = draw.save('').decode('utf-8')
        etype = None
        error = None
    except Exception, e:
        image = ''
        etype = e.__class__.__name__
        error = str(e)

    return dict(image=image, etype=etype, error=error)
