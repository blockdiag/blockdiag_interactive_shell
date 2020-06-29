var __last = null;
var compression = true;
var unicode_yensign_pattern = /^((?:[\x00-\x7F]|[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3})+)([\xa5])/;


function basename(path) {
  return path.replace(/\\/g,'/').replace( /.*\//, '' );
}
 
function dirname(path) {
  return path.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');
}


function render_version() {
  familyname = basename(dirname(document.URL));

  if (familyname == 'rackdiag' || familyname == 'packetdiag') {
    familyname = 'nwdiag';
  }

  $.ajax({
    url: '/static/versions.json',
    dataType: "json",
    success: function(json) {
      if (json[familyname]) {
        version = json[familyname];
      } else {
        version = json.blockdiag;
      }

      $('#version').text(' v' + version);
    }
  });
}

function adler32(str) {
  for (var base = 65521, lower = 1, upper = 0, index = 0, code;
       code = str.charCodeAt(index++);
       upper = (upper + lower) % base)
    lower = (lower + code) % base;

  var buf = new Array(4);
  buf[0] = String.fromCharCode(upper >> 8);
  buf[1] = String.fromCharCode(upper & 0xff);
  buf[2] = String.fromCharCode(lower >> 8);
  buf[3] = String.fromCharCode(lower & 0xff);
  return buf.join('');
}

function encode_diagram(diagram) {
  var diagram = Base64.utob(diagram);
  if (compression) {
     diagram = Base64.encodeURI('\x78\x9c' + RawDeflate.deflate(diagram) + adler32(diagram), true);
  } else {
     diagram = Base64.encodeURI(diagram);
  }
  return diagram;
}

class SVGtoPNGDataURL {
  constructor() {
    this.can = document.createElement('canvas'); // Not shown on page
    this.ctx = this.can.getContext('2d');
    this.loader = new Image; // Not shown on page
  }

  // Generate PNG data URL from SVG and send it to callback function when ready
  go(mySVG, callback) {
    var svgAsXML = (new XMLSerializer).serializeToString( mySVG );

    this.loader.width = this.can.width  = mySVG.clientWidth;
    this.loader.height = this.can.height = mySVG.clientHeight;
    var self = this;
    this.loader.onload = function() {
      self.ctx.drawImage( self.loader, 0, 0, self.loader.width, self.loader.height );
      callback(self.can.toDataURL());
    };
    this.loader.src = 'data:image/svg+xml,' + encodeURIComponent( svgAsXML );
  }
};

var pngconverter = new SVGtoPNGDataURL();

function update_diagram() {
  diagram = $('#diagram').val();
  if (diagram == null || diagram.length == 0) return;
  if (__last == diagram) return; 
  __last = diagram;

  while (diagram.match(unicode_yensign_pattern)) {
    diagram = diagram.replace(unicode_yensign_pattern, "$1\\");
  }

  if (compression) {
      params = "compression=deflate&";
  } else {
      params = "";
  }

  encoded_diagram = encode_diagram(diagram);
  $('#shorten_url a').attr('href', './?' + params + 'src=' + encoded_diagram);
  $('#download_url a').attr('href', './image?' + params + 'encoding=base64&src=' + encoded_diagram);

  if (Base64.encodeURI(diagram).length > 1400) {  // 1400 is magic number :-p
    $('#shorten_url a').addClass('disabled');
    $('#download_url a').addClass('disabled');
    $('#shorten_url a').removeAttr('href');
    $('#download_url a').removeAttr('href');
    $('#shorten_url span').show();
    $('#download_url span').show();
  } else {
    $('#shorten_url a').removeClass('disabled');
    $('#download_url a').removeClass('disabled');
    $('#shorten_url span').hide();
    $('#download_url span').hide();
    pngconverter.go($('#diagram_image svg'), callback=function(dataURL) {
      $('#download_url a#png_link').attr('href', dataURL);
    });
  }
  
  url = './image';
  params = {'encoding': 'jsonp', 'src': diagram};
  $.ajax({
    type: 'POST',
    url: url,
    dataType: "jsonp",
    data: params,
    error: function(XMLHtpRequest, textStatus, errorThrown) {
        msg = "ERROR: " + textStatus + '(' + XMLHttpRequest.status + '):' + errorThrown.message;
        $('#error_msg').text(msg);
        $('#error_msg').show();
    },
    success: function(json) {
      if (json['etype']) {
        msg = "ERROR: " + json['error'] + '(' + json['etype'] + ')';
        $('#error_msg').text(msg);
        $('#error_msg').show();
      } else if (json['image'] != "") {
        $('#error_msg').hide()

        re = RegExp('viewBox="\\d+\\s+\\d+\\s+(\\d+)\\s+(\\d+)\\s*"');
        m = json['image'].match(re);
        if (m) {
          width = m[1]
          height = m[2]
        } else {
          width = 400
          height = 400
        }

        html = json['image'].replace(/<\?xml.*>\n/, '')
        html = html.replace(/<!DOCTYPE.*>\n/, '')
        $('#diagram_image').html(html);

        is_webkit = !document.uniqueID && !window.opera && !window.sidebar && window.localStorage && typeof window.orientation == "undefined";
        if (is_webkit) {
          // for Chrome and Safari
          $('#diagram_image svg').removeAttr('viewBox');
          $('#diagram_image svg').width(width);
          $('#diagram_image svg').height(height);
        }
      }
    }
  });
}


/* parse arguments */
var args = [], arg;
var parsed = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
for(var i = 0; i < parsed.length; i++) { 
  arg = parsed[i].split('='); 
  args.push(arg[0]);
  args[arg[0]] = arg[1];
}


$(document).ready(function($){
  diagram = $('#diagram');
  diagram.timer = null;

  source = args.src;
  if (source) {
    source = Base64.decode(source, true);

    if (args.compression == 'deflate') {
      source = Base64.utob(source);
      // ignore the header and the checksum
      source = source.substring(2, source.length - 4);
      source = RawDeflate.inflate(source);

      source = Base64.btou(source);
    }

    diagram.val(source);
  }

  diagram.bind('keyup change', function(){
    if (diagram.timer)  clearTimeout(diagram.timer);

    diagram.timer = setTimeout(update_diagram, 500);
  });

  render_version();
  update_diagram();
});
