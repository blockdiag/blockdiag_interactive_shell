var __last = null;
var unicode_yensign_pattern = /^((?:[\x00-\x7F]|[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3})+)([\xa5])/;


function basename(path) {
  return path.replace(/\\/g,'/').replace( /.*\//, '' );
}
 
function dirname(path) {
  return path.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');
}


function render_version() {
  familyname = basename(dirname(document.URL));

  if (familyname == 'rackdiag') {
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
  return Base64.encodeURI('\x78\x9c' + RawDeflate.deflate(diagram) + adler32(diagram));
}

function update_diagram() {
  diagram = $('#diagram').val();
  if (diagram == null || diagram.length == 0) return;
  if (__last == diagram) return; 
  __last = diagram;

  while (diagram.match(unicode_yensign_pattern)) {
    diagram = diagram.replace(unicode_yensign_pattern, "$1\\");
  }

  encoded_diagram = encode_diagram(diagram);
  if (encoded_diagram > 2000) {
    msg = "ERROR: source diagram is too long. Interactive shell does not support large diagram, Try using command-line's."
    $('#error_msg').text(msg);
    $('#error_msg').show();
    return;
  }

  $('#shorten_url a').attr('href', './?compression=deflate&src=' + encoded_diagram)
  $('#download_url a').attr('href', './image?compression=deflate&encoding=base64&src=' + encoded_diagram)

  url = './image';
  params = {'encoding': 'jsonp', 'src': diagram};
  $.ajax({
    url: url,
    dataType: "jsonp",
    data: params,
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

        is_webkit = !document.uniqueID && !window.opera && !window.globalStorage && window.localStorage
        if (!is_webkit && jQuery.support.noCloneEvent && !window.globalStorage){
          url = './image?compression=deflate&encoding=base64&src=' + encoded_diagram
          var obj = $(document.createElement('object'))
          obj.attr('type', 'image/svg+xml')
          obj.attr('data', url)
          obj.attr('width', width)
          obj.attr('height', height)
          $('#diagram_image').html(obj);
        } else {
          html = json['image'].replace(/<\?xml.*>\n/, '')
          html = html.replace(/<!DOCTYPE.*>\n/, '')

          $('#diagram_image').html(html);
          if (is_webkit) {
            // for Chrome and Safari
            $('#diagram_image svg').removeAttr('viewBox');
            $('#diagram_image svg').width(width);
            $('#diagram_image svg').height(height);
          }
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
    source = Base64.decode(source)

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
