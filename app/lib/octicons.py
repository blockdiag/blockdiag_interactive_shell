# -*- coding: utf-8 -*-
#  Copyright 2014 Takeshi KOMIYA
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

import os
import re
from PIL import Image, ImageDraw, ImageFont, PILLOW_VERSION
from blockdiag import plugins
from blockdiag.utils import unquote
from blockdiag.utils.logging import warning

icons = {
    'alert': u'\uf02d',
    'alignment-align': u'\uf08a',
    'alignment-aligned-to': u'\uf08e',
    'alignment-unalign': u'\uf08b',
    'arrow-down': u'\uf03f',
    'arrow-left': u'\uf040',
    'arrow-right': u'\uf03e',
    'arrow-small-down': u'\uf0a0',
    'arrow-small-left': u'\uf0a1',
    'arrow-small-right': u'\uf071',
    'arrow-small-up': u'\uf09f',
    'arrow-up': u'\uf03d',
    'beer': u'\uf069',
    'book': u'\uf007',
    'bookmark': u'\uf07b',
    'briefcase': u'\uf0d3',
    'broadcast': u'\uf048',
    'browser': u'\uf0c5',
    'bug': u'\uf091',
    'calendar': u'\uf068',
    'check': u'\uf03a',
    'checklist': u'\uf076',
    'chevron-down': u'\uf0a3',
    'chevron-left': u'\uf0a4',
    'chevron-right': u'\uf078',
    'chevron-up': u'\uf0a2',
    'circle-slash': u'\uf084',
    'circuit-board': u'\uf0d6',
    'clippy': u'\uf035',
    'clock': u'\uf046',
    'cloud-download': u'\uf00b',
    'cloud-upload': u'\uf00c',
    'code': u'\uf05f',
    'color-mode': u'\uf065',
    'comment-add': u'\uf02b',
    'comment': u'\uf02b',
    'comment-discussion': u'\uf04f',
    'credit-card': u'\uf045',
    'dash': u'\uf0ca',
    'dashboard': u'\uf07d',
    'database': u'\uf096',
    'device-camera': u'\uf056',
    'device-camera-video': u'\uf057',
    'device-desktop': u'\uf27c',
    'device-mobile': u'\uf038',
    'diff': u'\uf04d',
    'diff-added': u'\uf06b',
    'diff-ignored': u'\uf099',
    'diff-modified': u'\uf06d',
    'diff-removed': u'\uf06c',
    'diff-renamed': u'\uf06e',
    'ellipsis': u'\uf09a',
    'eye-unwatch': u'\uf04e',
    'eye-watch': u'\uf04e',
    'eye': u'\uf04e',
    'file-binary': u'\uf094',
    'file-code': u'\uf010',
    'file-directory': u'\uf016',
    'file-media': u'\uf012',
    'file-pdf': u'\uf014',
    'file-submodule': u'\uf017',
    'file-symlink-directory': u'\uf0b1',
    'file-symlink-file': u'\uf0b0',
    'file-text': u'\uf011',
    'file-zip': u'\uf013',
    'flame': u'\uf0d2',
    'fold': u'\uf0cc',
    'gear': u'\uf02f',
    'gift': u'\uf042',
    'gist': u'\uf00e',
    'gist-secret': u'\uf08c',
    'git-branch-create': u'\uf020',
    'git-branch-delete': u'\uf020',
    'git-branch': u'\uf020',
    'git-commit': u'\uf01f',
    'git-compare': u'\uf0ac',
    'git-merge': u'\uf023',
    'git-pull-request-abandoned': u'\uf009',
    'git-pull-request': u'\uf009',
    'globe': u'\uf0b6',
    'graph': u'\uf043',
    'heart': u'\2665',
    'history': u'\uf07e',
    'home': u'\uf08d',
    'horizontal-rule': u'\uf070',
    'hourglass': u'\uf09e',
    'hubot': u'\uf09d',
    'inbox': u'\uf0cf',
    'info': u'\uf059',
    'issue-closed': u'\uf028',
    'issue-opened': u'\uf026',
    'issue-reopened': u'\uf027',
    'jersey': u'\uf019',
    'jump-down': u'\uf072',
    'jump-left': u'\uf0a5',
    'jump-right': u'\uf0a6',
    'jump-up': u'\uf073',
    'key': u'\uf049',
    'keyboard': u'\uf00d',
    'law': u'\uf0d8',
    'light-bulb': u'\uf000',
    'link': u'\uf05c',
    'link-external': u'\uf07f',
    'list-ordered': u'\uf062',
    'list-unordered': u'\uf061',
    'location': u'\uf060',
    'gist-private': u'\uf06a',
    'mirror-private': u'\uf06a',
    'git-fork-private': u'\uf06a',
    'lock': u'\uf06a',
    'logo-github': u'\uf092',
    'mail': u'\uf03b',
    'mail-read': u'\uf03c',
    'mail-reply': u'\uf051',
    'mark-github': u'\uf00a',
    'markdown': u'\uf0c9',
    'megaphone': u'\uf077',
    'mention': u'\uf0be',
    'microscope': u'\uf089',
    'milestone': u'\uf075',
    'mirror-public': u'\uf024',
    'mirror': u'\uf024',
    'mortar-board': u'\uf0d7',
    'move-down': u'\uf0a8',
    'move-left': u'\uf074',
    'move-right': u'\uf0a9',
    'move-up': u'\uf0a7',
    'mute': u'\uf080',
    'no-newline': u'\uf09c',
    'octoface': u'\uf008',
    'organization': u'\uf037',
    'package': u'\uf0c4',
    'paintcan': u'\uf0d1',
    'pencil': u'\uf058',
    'person-add': u'\uf018',
    'person-follow': u'\uf018',
    'person': u'\uf018',
    'pin': u'\uf041',
    'playback-fast-forward': u'\uf0bd',
    'playback-pause': u'\uf0bb',
    'playback-play': u'\uf0bf',
    'playback-rewind': u'\uf0bc',
    'plug': u'\uf0d4',
    'repo-create': u'\uf05d',
    'gist-new': u'\uf05d',
    'file-directory-create': u'\uf05d',
    'file-add': u'\uf05d',
    'plus': u'\uf05d',
    'podium': u'\uf0af',
    'primitive-dot': u'\uf052',
    'primitive-square': u'\uf053',
    'pulse': u'\uf085',
    'puzzle': u'\uf0c0',
    'question': u'\uf02c',
    'quote': u'\uf063',
    'radio-tower': u'\uf030',
    'repo-delete': u'\uf001',
    'repo': u'\uf001',
    'repo-clone': u'\uf04c',
    'repo-force-push': u'\uf04a',
    'gist-fork': u'\uf002',
    'repo-forked': u'\uf002',
    'repo-pull': u'\uf006',
    'repo-push': u'\uf005',
    'rocket': u'\uf033',
    'rss': u'\uf034',
    'ruby': u'\uf047',
    'screen-full': u'\uf066',
    'screen-normal': u'\uf067',
    'search-save': u'\uf02e',
    'search': u'\uf02e',
    'server': u'\uf097',
    'settings': u'\uf07c',
    'log-in': u'\uf036',
    'sign-in': u'\uf036',
    'log-out': u'\uf032',
    'sign-out': u'\uf032',
    'split': u'\uf0c6',
    'squirrel': u'\uf0b2',
    'star-add': u'\uf02a',
    'star-delete': u'\uf02a',
    'star': u'\uf02a',
    'steps': u'\uf0c7',
    'stop': u'\uf08f',
    'repo-sync': u'\uf087',
    'sync': u'\uf087',
    'tag-remove': u'\uf015',
    'tag-add': u'\uf015',
    'tag': u'\uf015',
    'telescope': u'\uf088',
    'terminal': u'\uf0c8',
    'three-bars': u'\uf05e',
    'tools': u'\uf031',
    'trashcan': u'\uf0d0',
    'triangle-down': u'\uf05b',
    'triangle-left': u'\uf044',
    'triangle-right': u'\uf05a',
    'triangle-up': u'\uf0aa',
    'unfold': u'\uf039',
    'unmute': u'\uf0ba',
    'versions': u'\uf064',
    'remove-close': u'\uf081',
    'x': u'\uf081',
    'zap': u'\26A1',
}
prefix = re.compile('^octicon://(\S+?)(?:\?(\S+))?$')
image_size_def = {'small': 16, 'normal': 32, 'large': 64}
fontpath = os.path.splitext(__file__)[0] + '.ttf'

icon_images = {}


def to_option(options):
    if options is None:
        return {}

    return dict(arg.split('=') for arg in options.split('&'))


def get_image_size(options):
    image_size = options.get('size', 'normal').lower()
    try:
        r = int(image_size)
    except:
        r = image_size_def.get(image_size)
        if r is None:
            warning('unknown image size: %s', image_size)
            r = image_size_def.get('normal')

    return r


class OcticonPlugin(plugins.NodeHandler):
    def on_attr_changing(self, node, attr):
        if attr.name not in ('background', 'icon'):
            return True

        value = unquote(attr.value)
        matched = prefix.match(value)
        if not matched:
            return True

        code = icons.get(matched.group(1))
        if code is None:
            warning('unknown octicon: %s', value)
            setattr(node, attr.name, None)
            return False

        if value not in icon_images:
            options = to_option(matched.group(2))
            image = self.create_octicon_image(code, options)
            icon_images[value] = image

        setattr(node, attr.name, icon_images[value])
        return False

    def create_octicon_image(self, iconcode, options):
        r = get_image_size(options)
        font = ImageFont.truetype(fontpath, r)
        textsize = font.getsize(iconcode)

        # Avoid offset problem in Pillow (>= 2.2.0, < 2.6.0)
        if "2.2.0" <= PILLOW_VERSION < "2.6.0":
            offset = font.getoffset(iconcode)
            textsize = (textsize[0] + offset[0], textsize[1] + offset[1])

        image = Image.new('RGBA', textsize)
        drawer = ImageDraw.Draw(image)
        drawer.text((0, 0), iconcode,
                    fill=options.get('color', 'black'), font=font)
        return image


def on_cleanup():
    for key, image in icon_images.items():
        image.close()
        del icon_images[key]


def setup(self, diagram, **kwargs):
    plugins.install_node_handler(OcticonPlugin(diagram, **kwargs))
    plugins.install_general_handler('cleanup', on_cleanup)
