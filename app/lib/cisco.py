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
from blockdiag.noderenderer import NodeShape
from blockdiag.noderenderer import install_renderer
from blockdiag.utils.XY import XY

try:
    from blockdiag.utils.PILTextFolder import PILTextFolder as TextFolder
except ImportError:
    from blockdiag.utils.TextFolder import TextFolder


def gen_image_class(image_path, baseurl=None):
    if baseurl:
        image_url = "%s/%s" % (baseurl, os.path.basename(image_path))
    else:
        image_url = image_path

    class CiscoImage(NodeShape):
        def __init__(self, node, metrix=None):
            super(CiscoImage, self).__init__(node, metrix)

            self.textalign = 'left'
            self.image_path = image_path

            size = self.image_size

            pt = metrix.cell(node).center()
            self.image_box = [pt.x - size[0] / 2, pt.y - size[1] / 2,
                              pt.x + size[0] / 2, pt.y + size[1] / 2]

            width = metrix.nodeWidth / 2 - size[0] / 2 + metrix.cellSize
            self.textbox = [pt.x + size[0] / 2, pt.y - size[1] / 2,
                            pt.x + size[0] / 2 + width, pt.y + size[1] / 2]

            folder = TextFolder(self.textbox, node.label,
                                halign=self.textalign,
                                font=self.metrix.font,
                                fontsize=self.metrix.fontSize)
            textbox = folder.outlineBox()

            self.connectors[0] = XY(pt.x, self.image_box[1])
            self.connectors[1] = XY(textbox[2] + self.metrix.nodePadding, pt.y)
            self.connectors[2] = XY(pt.x, self.image_box[3])
            self.connectors[3] = XY(self.image_box[0], pt.y)

        @property
        def image_size(self):
            try:
                import PIL.Image
                raise ImportError()

                size = PIL.Image.open(image_path).size
            except ImportError:
                size = JpegFile.get_size(image_path)

            box = [self.metrix.nodeWidth, self.metrix.nodeHeight]

            if box[0] < size[0] or box[1] < size[1]:
                if (size[0] * 1.0 / box[0]) < (size[1] * 1.0 / box[1]):
                    size = (size[0] * box[1] / size[1], box[1])
                else:
                    size = (box[0], size[1] * box[0] / size[0])

            return size

        def render_shape(self, drawer, format, **kwargs):
            if not kwargs.get('shadow'):
                drawer.loadImage(image_url, self.image_box)

    return CiscoImage


class StreamReader(object):
    def __init__(self, stream):
        self.stream = stream
        self.pos = 0

    def read_byte(self):
        byte = self.stream[self.pos]
        self.pos += 1
        return ord(byte)

    def read_word(self):
        byte1, byte2 = self.stream[self.pos:self.pos + 2]
        self.pos += 2
        return (ord(byte1) << 8) + ord(byte2)

    def read_bytes(self, n):
        bytes = self.stream[self.pos:self.pos + n]
        self.pos += n
        return bytes


class JpegHeaderReader(StreamReader):
    M_SOI = 0xd8
    M_SOS = 0xda

    def read_marker(self):
        if self.read_byte() != 255:
            raise ValueError("error reading marker")
        return self.read_byte()

    def skip_marker(self):
        """Skip over an unknown or uninteresting variable-length marker"""
        length = self.read_word()
        self.read_bytes(length - 2)

    def __iter__(self):
        while True:
            if self.read_byte() != 255:
                raise ValueError("error reading marker")

            marker = self.read_byte()
            if marker == self.M_SOI:
                length = 0
                data = ''
            else:
                length = self.read_word()
                data = self.read_bytes(length - 2)

            yield (marker, data)

            if marker == self.M_SOS:
                raise StopIteration()


class JpegFile(object):
    M_SOF0 = 0xc0
    M_SOF1 = 0xc1

    @classmethod
    def get_size(self, filename):
        image = open(filename, 'rb').read()
        headers = JpegHeaderReader(image)
        for header in headers:
            if header[0] in (self.M_SOF0, self.M_SOF1):
                data = header[1]

                height = (ord(data[1]) << 8) + ord(data[2])
                width = (ord(data[3]) << 8) + ord(data[4])
                return (width, height)


def to_classname(filename):
    filename = re.sub('\.[a-z]+$', '', filename)
    filename = re.sub(' ', '_', filename)

    return "cisco.%s" % filename


def setup(self, baseurl=None):
    path = "%s/images/cisco" % os.path.dirname(__file__)
    dir = os.listdir(path)
    for filename in dir:
        klass = gen_image_class("%s/%s" % (path, filename), baseurl)
        klassname = to_classname(filename)

        install_renderer(klassname, klass)
