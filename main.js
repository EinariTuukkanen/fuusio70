
$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

$(function() {
    $('form').submit(function() {
        var formData = $('form').serializeObject();
        var url = "http://localhost:5000/users";
        var method = "POST";
        var postData = JSON.stringify(formData);

        var async = false;

        var request = new XMLHttpRequest();

        request.onload = function () {

           var status = request.status; // HTTP response status, e.g., 200 for "200 OK"
           var data = request.responseText; // Returned data, e.g., an HTML document.
           console.debug('done', data);
        }

        request.open(method, url, async);

        request.send(postData);
        return false;
    });
});
