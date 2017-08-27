
$(document).ready(function() {
  // get current URL path and assign 'active' class
  var pathname = window.location.pathname;
  $('.nav > li > a[href="' + pathname + '"]').parent().addClass('active');
});

$(document).ready(function() {
  $('#datatables').DataTable();
});

// external site warning
$('a.warn-external').on('click', function(event) {
  event.preventDefault();
  var $tooltips = $('[data-toggle="tooltip"]');
  var link = event.target.href;
  if (!link) {
    link = event.target.parentNode.href; // because sometimes the event registers as the p instead of the a
  }
  swal({
    title: 'Heads Up!',
    html: '<p>The link you clicked leads to a page outside of this portal.</p>' +
    '<a href="' + link + '" class="btn btn-info btn-wd" target="_blank" onclick="swal.clickCancel()">Take me Anyway</a>' +
    '<a href="#" class="btn btn-warning btn-wd" onclick="swal.clickCancel()" >Nevermind</a>',
    type: 'warning',
    showCancelButton: false,
    showConfirmButton: false,
    buttonsStyling: false
  }).then( function() { },
  function(dismiss) {
    if (dismiss === 'cancel' || dismiss === 'overlay' || dismiss === 'esc') {
      $tooltips.tooltip('hide'); // hide bootstrap tooltips after the modal closes
    }
  });
});

// Google Analytics Tracking Code
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-75293029-2', 'auto');
  ga('send', 'pageview');
