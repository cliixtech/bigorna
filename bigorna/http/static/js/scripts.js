// Empty JS for your own code to be here
var showOutput = function (url) {
    $.ajax({
        url: url,
        context: document.body
      }).done(function(data) {
          $('#outputContent').text(data);
          $('#outputModal').modal('show');
      });
};
