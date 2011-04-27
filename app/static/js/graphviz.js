var __last = null;

function update_diagram() {
  diagram = $('#diagram').val();
  if (diagram == null || diagram.length == 0) return;
  if (__last == diagram) return; 
  __last = diagram;

  encoded_diagram = Base64.encodeURI(diagram)
  url = './?src=' + encoded_diagram
  $('#shorten_url a').attr('href', url)

  stripped_diagram = diagram.replace(/\s/g, '')

  url = 'https://chart.googleapis.com/chart?callback=?';
  params = {'cht': 'gv', 'chof': 'json', 'chl': stripped_diagram};
  $.ajax({
    url: url,
    dataType: "jsonp",
    data: params,
    success: function(json) {
      url = 'https://chart.googleapis.com/chart?cht=gv&amp;chl=' +
            escape(stripped_diagram);
      html = '<img src="' + url + '" />'
      $('#diagram_image').html(html);
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
