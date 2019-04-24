$(document).ready(function(){

$.get('/entries', function(data, status){
    var source = $('#entries-template').html();
    var template = Handlebars.compile(source);
    var html = template(data);
    $('#entries-table').html(html);
});

});
