# -*- coding: utf-8 -*-
from lib.utils import base64_decode, get_redirect_url, simplejson
from flask import Blueprint, redirect, request, make_response, render_template

app = Blueprint('blockdiag_main', __name__)


@app.route('/')
def blockdiag_index():
    import blockdiag
    kwargs = {'version': blockdiag.__version__}

    url = get_redirect_url('', request)
    if url:
        return redirect(url)

    source = request.args.get('src')
    if source:
        kwargs['diagram'] = base64_decode(source)

    body = render_template('blockdiag.html', **kwargs)
    response = make_response(body)
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

    image = blockdiag_generate_image(source)
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
        if encoding == 'base64':
            response.headers['Content-Type'] = 'image/svg+xml'
        else:
            response.headers['Content-Type'] = 'text/plain'

    return response


def blockdiag_generate_image(source):
    from blockdiag import diagparser, builder, DiagramDraw
    from blockdiag.elements import DiagramNode, DiagramEdge, NodeGroup

    try:
        tree = diagparser.parse_string(source)
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = DiagramDraw.DiagramDraw('SVG', diagram)
        draw.draw()

        svg = draw.save('').decode('utf-8')
        etype = None
        error = None
    except Exception, e:
        svg = ''
        etype = e.__class__.__name__
        error = str(e)

    return dict(image=svg, etype=etype, error=error)


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
        response = make_response(body)
        response.headers['Content-Type'] = 'application/xhtml+xml'
        return response


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
