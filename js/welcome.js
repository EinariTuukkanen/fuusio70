
// ============================
// >> WELCOME PAGE
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
            var url = location.href.split('/');
            url.pop();
            location.href = url.join('/') + '/registration.html';
        },
        error: function(response) {
            console.error('ERROR', response);
           
        },
    });
}

function toRegistration() {
    var userId = localStorage.getItem('fuusioUserId');
    console.debug('local', API_USERS_URL + '/' + userId);
    if (!!userId) {
        $.ajax({
            url: API_USERS_URL + '/' + userId,
            type: "GET",
            contentType: 'application/json',
            cache: false,
            success: function(response) {
                var data = JSON.parse(response);
                var timestamp = Math.floor(Date.now() / 1000);
                var diff = timestamp - data.timestamp;

                // 30 min timeout
                if (diff > 1) {
                    localStorage.removeItem('fuusioUserId');
                    createUser();
                }
                console.debug(data);
            },
            error: function(response) {
                console.error('ERROR', response);
            },
        });

    } else {
       createUser();
    }
     
}

// Helper function to insert users in html table
function insertUserToTable(index, table, user) {
    var row = table.insertRow(-1);
    var cellIndex = row.insertCell(0);
    var cellName = row.insertCell(1);
    var cellTable = row.insertCell(2);

    cellIndex.innerHTML = index;
    cellName.innerHTML = user.name;
    cellTable.innerHTML = user.table;
}

// On page load get users and insert them to table
$(function() {
    var table = document.getElementById('registeredUsers');
    $.ajax({
        url: API_USERS_URL,
        type: "GET",
        cache: false,
        success: function(response) {
            var usersData = JSON.parse(response);
            for (var i = 0; i < usersData.length; i++) {
                insertUserToTable(i + 1, table, usersData[i]);
            }
       
        },
        error: function(response) {
            console.error('ERROR', response);
   
        },
    });
});
