


// ============================
// >> REGISTRATION FORM
// ============================

function createUser() {
     $.ajax({
        url: API_USERS_URL,
        type: "POST",
        contentType: 'application/json',
        cache: false,
        success: function(response) {
            var data = JSON.parse(response);
            localStorage.setItem('fuusioUserId', data.userId);
        },
        error: function(response) {
            console.error('ERROR', response);
        },
    });
}


$(function() {
    var userId = localStorage.getItem('fuusioUserId');
    if (!!userId) {
        $.ajax({
            url: API_USERS_URL + '/' + userId,
            type: "GET",
            contentType: 'application/json',
            cache: false,
            success: function(response) {
                
                var data = JSON.parse(response);
                if (!data) {
                    localStorage.removeItem('fuusioUserId');
                    console.debug('Invalid userid!');
                    createUser()
                    return
                }
                var timestamp = Math.floor(Date.now() / 1000);
                var diff = timestamp - data.timestamp;

                // 30 min timeout
                if (diff > 1800) {
                    localStorage.removeItem('fuusioUserId');
                    console.debug('Timeout!');
                    createUser();
                }
                var leftMins =  parseInt(30 - diff/60);
                console.debug('Still time left: ', leftMins);
                console.debug(data);

                $('#registrationInfo').text(
                    'Olet jonossa sijalla 1, täytä ilmoittautumislomake alla vahvistaaksesi ilmoittautumisen. ' +
                    'Sinulla on ' +  leftMins + ' minuuttia aikaa ennen lomakkeen vanhentumista.'
                );
            },
            error: function(response) {
                console.error('ERROR', response);
            },
        });

    } else {
       createUser();
    }
});



// Floating label headings for the registration form
$(function() {
    $("body").on("input propertychange", ".floating-label-form-group", function(e) {
        $(this).toggleClass("floating-label-form-group-with-value", !!$(e.target).val());
    }).on("focus", ".floating-label-form-group", function() {
        $(this).addClass("floating-label-form-group-with-focus");
    }).on("blur", ".floating-label-form-group", function() {
        $(this).removeClass("floating-label-form-group-with-focus");
    });
});


// Helper to convert formData to object
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

// Form validator
$(function() {

    $("#registrationForm input,#registrationForm textarea").jqBootstrapValidation({
        preventSubmit: true,
        submitError: function($form, event, errors) {
            // additional error messages or events
        },
        submitSuccess: function($form, event) {
            event.preventDefault(); // prevent default submit behaviour
            // get values from FORM
            var name = $("input#name").val();
            // var email = $("input#email").val();
            // var phone = $("input#phone").val();
            // var message = $("textarea#message").val();
            var formData = $('form').serializeObject();

            console.debug('formData: ', formData);

            var userId = localStorage.getItem('fuusioUserId');

            if (!userId) {
                console.debug('Userid not found!');
                return
            }
            var data = {formData: formData, userId: userId};

            $.ajax({
                url: API_USERS_URL,
                type: "PUT",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify(data),
                cache: false,
                success: function(response) {
                    console.debug(response);
                    // Success message
                    $('#success').html("<div class='alert alert-success'>");
                    $('#success > .alert-success').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-success')
                        .append("<strong>Ilmoittautumisesi on vastaanotettu. </strong>");
                    $('#success > .alert-success')
                        .append('</div>');


                    $('#submitForm').hide();

                    //clear all fields
                    $('#registrationForm').trigger("reset");
                },
                error: function(response) {
                    console.error('ERROR', response);
                    // Fail message
                    $('#success').html("<div class='alert alert-danger'>");
                    $('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-danger').append("<strong>Pahoittelut, palvelin ei vastaa, yritä myöhemmin uudestaan!</strong>");
                    $('#success > .alert-danger').append('</div>');


                    //clear all fields
                    $('#registrationForm').trigger("reset");
                },
            });
        },
        filter: function() {
            return $(this).is(":visible");
        },
    });

    $("a[data-toggle=\"tab\"]").click(function(e) {
        e.preventDefault();
        $(this).tab("show");
    });
});


/*When clicking on Full hide fail/success boxes */
$('#name').focus(function() {
    $('#success').html('');
});
