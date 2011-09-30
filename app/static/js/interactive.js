var __last = null;
var unicode_yensign_pattern = /^((?:[\x00-\x7F]|[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3})+)([\xa5])/;

function update_diagram() {
  diagram = $('#diagram').val();
  if (diagram == null || diagram.length == 0) return;
  if (__last == diagram) return; 
  __last = diagram;

  while (diagram.match(unicode_yensign_pattern)) {
    diagram = diagram.replace(unicode_yensign_pattern, "$1\\");
  }

  encoded_diagram = Base64.encodeURI(diagram)
  if (encoded_diagram > 2000) {
    msg = "ERROR: source diagram is too long. Interactive shell does not support large diagram, Try using command-line's."
    $('#error_msg').text(msg);
    $('#error_msg').show();
    return;
  }

  $('#shorten_url a').attr('href', './?src=' + encoded_diagram)
  $('#download_url a').attr('href', './image?encoding=base64&src=' + encoded_diagram)

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

        if (jQuery.support.checkOn && jQuery.support.noCloneEvent && !window.globalStorage){
          encoded_diagram = Base64.encodeURI(diagram)
          url = './image?encoding=base64&src=' + encoded_diagram
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
          if (!$.support.checkOn) {
            // for Chrome and Safari
            $('#diagram_image svg').removeAttr('viewBox');
            $('#diagram_image svg').attr('width', width);
            $('#diagram_image svg').attr('height', height);
          }
        }
      }
    }
  });
}

$(document).ready(function($){
  diagram = $('#diagram');
  diagram.timer = null;

  diagram.bind('keyup change', function(){
    if (diagram.timer)  clearTimeout(diagram.timer);

    diagram.timer = setTimeout(update_diagram, 500);
  });

  update_diagram();
});
