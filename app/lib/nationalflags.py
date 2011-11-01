# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
import os
from blockdiag.noderenderer import install_renderer
from blockdiag.noderenderer.box import Box
from blockdiag.utils import images, XY

try:
    from blockdiag.utils.PILTextFolder import PILTextFolder as TextFolder
except ImportError:
    from blockdiag.utils.TextFolder import TextFolder


def gen_image_class(image_path, baseurl=None):
    if baseurl:
        image_url = "%s/%s" % (baseurl, os.path.basename(image_path))
    else:
        image_url = image_path

    class NationalFlagImage(Box):
        def __init__(self, node, metrics=None):
            super(NationalFlagImage, self).__init__(node, metrics)

            self.textalign = 'left'
            self.image_path = image_path

            box = metrics.cell(node).box
            bounded = (box[2] - box[0], box[3] - box[1])
            size = images.get_image_size(image_path)
            size = images.calc_image_size(size, bounded)

            pt = metrics.cell(node).center
            self.image_box = [pt.x - size[0] / 2, pt.y - size[1] / 2,
                              pt.x + size[0] / 2, pt.y + size[1] / 2]

            width = metrics.node_width / 2 - size[0] / 2 + metrics.cellsize
            self.textbox = [pt.x + size[0] / 2, pt.y - size[1] / 2,
                            pt.x + size[0] / 2 + width, pt.y + size[1] / 2]

            folder = TextFolder(self.textbox, node.label,
                                halign=self.textalign,
                                font=self.metrics.font,
                                fontsize=self.metrics.fontsize)
            textbox = folder.outlinebox

            self.connectors[0] = XY(pt.x, self.image_box[1])
            self.connectors[1] = XY(textbox[2] + self.metrics.node_padding, pt.y)
            self.connectors[2] = XY(pt.x, self.image_box[3])
            self.connectors[3] = XY(self.image_box[0], pt.y)

        def render_shape(self, drawer, format, **kwargs):
            if not kwargs.get('shadow'):
                drawer.loadImage(image_url, self.image_box)
                drawer.rectangle(self.image_box, outline='black')

    return NationalFlagImage


def to_classname(filename):
    #137px-Flag_of_Lithuania.svg.png 
    filename = re.sub('.svg.png', '', filename)
    filename = re.sub('.*Flag_of_', '', filename)
    filename = re.sub('-', '_', filename)

    return "nationalflag.%s" % filename.lower()


def setup(self, baseurl=None):
    path = "%s/images/nationalflags" % os.path.dirname(__file__)
    dir = os.listdir(path)
    for filename in dir:
        klass = gen_image_class("%s/%s" % (path, filename), baseurl)
        klassname = to_classname(filename)

        install_renderer(klassname, klass)
