window.onload = function() {
  var timeline_toggle = document.getElementById('timeline_toggle');
  var s = new io.Socket(window.location.hostname, {
    port: 8000,
    resource: 'fistatus',
    rememberTransport: false,
    transports: [
      'websocket',
      'xhr-multipart',
      'xhr-polling'
    ]
  });
  s.connect();
  var audio_alert = document.getElementById('alarm');

  s.addEvent('message', function(data) {
    js_data = $.parseJSON(data);
    var prettyName = js_data.name.replace(/_and_/g, '&').replace(/_/g, ' ');
    var d = new Date();
    $('#messages').text('Last Update: ' + d.format("dddd, mmmm dS, yyyy, h:MM:ss TT"));
    
    if (js_data.status == 'GREEN') {
      $('#' + js_data.name).css('background-color', '#00CC33');
      var text = '<div class="filog">'+d.format('h:MM:ss TT')+': <font color="#009933"><b>'+prettyName+'</b></font></div>';
      $('#fiSlideIn').prepend(text);
    }
    else if (js_data.status == 'AMBER') {
      $('#' + js_data.name).css('background-color', '#FFFF00');
      var text = '<div class="filog">'+d.format('h:MM:ss TT')+': <font color="#C68E17"><b>'+prettyName+'</b></font></div>';
      $('#fiSlideIn').prepend(text);
    }
    else if (js_data.status == 'RED') {
      $('#' + js_data.name).css('background-color', '#F00000');
      var text = '<div class="filog">'+d.format('h:MM:ss TT')+': <font color="#C00000"><b>'+prettyName+'</b></font></div>';
      $('#fiSlideIn').prepend(text);
      if (js_data.alarm == 'ON') {
        audio_alert.play();
      }
    }
  });

  timeline_toggle.onclick = function(e) {
    e.preventDefault()
    if ($('#fiSlideIn').css('display') == 'block') {
      $('#tableWrapper').css('width', '100%');
      $('#fiSlideIn').css('display', 'none');
    }
    else {
      $('#tableWrapper').css('width', '80%');
      $('#fiSlideIn').css('display', 'block');
    }
    return false;
  }
};