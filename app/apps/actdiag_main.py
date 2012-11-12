# -*- coding: utf-8 -*-
from lib.utils import decode_source, get_redirect_url, get_fontmap, simplejson
from flask import Blueprint, redirect, request, make_response, render_template

app = Blueprint('actdiag_main', __name__)


@app.route('/')
def actdiag_index():
    import actdiag
    kwargs = {'version': actdiag.__version__}

    url = get_redirect_url('actdiag', request)
    if url:
        return redirect(url)

    source = request.args.get('src')
    if source:
        compression = request.args.get('compression')
        kwargs['diagram'] = decode_source(source, 'base64', compression)

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
    compression = request.args.get('compression')

    source = decode_source(source, encoding, compression)

    format = request.args.get('format', 'SVG')
    image = actdiag_generate_image(source, format)
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


def actdiag_generate_image(source, format):
    import actdiag
    from actdiag import parser, builder, drawer

    try:
        tree = parser.parse_string(source)
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = drawer.DiagramDraw(format, diagram, fontmap=get_fontmap(),
                                  ignore_pil=True)
        draw.draw()

        image = draw.save().decode('utf-8')
        etype = None
        error = None
    except Exception, e:
        image = ''
        etype = e.__class__.__name__
        error = str(e)

    return dict(image=image, etype=etype, error=error)
