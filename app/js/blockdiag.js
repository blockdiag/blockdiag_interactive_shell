var __last = null;

function update_diagram() {
  diagram = $('#diagram').val();
  if (diagram == null || diagram.length == 0) return;
  if (__last == diagram) return; 
  __last = diagram;

  url = 'http://blockdiag.appspot.com/image';
  params = {'src': diagram};
  $.post(url, params, function(data, status){
    if (status == 'success' && data != "\n") {
      html = data.replace(/<\?xml.*>\n/, '')
      html = html.replace(/<!DOCTYPE.*>\n/, '')

      $('#diagram_image').html(html);
      if (!$.support.checkOn) {
        // for Chrome and Safari
        $('#diagram_image svg').removeAttr('viewBox');
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
