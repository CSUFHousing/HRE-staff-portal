var f = $('.btn-form-link');
f.each( function () {
  var a = $(this).attr('href');
  var b = a + '?entry={"ContactInformation":{"Name":{"First":"{{ request.user.first_name }}", "Last":"{{ request.user.last_name }}"}, "Phone":"{{ request.user.employee.phone }}", "Email":"{{ request.user.email }}"}}';
  $(this).attr('href', b);
});

$(document).ready( function () {
  $('#loading').toggle();
  $('#main').toggle();
});
