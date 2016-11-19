var API_BASE_URL = 'http://138.68.91.244:5000'; // 138.68.91.244:5000

// ============================
// >> WELCOME PAGE
// ============================


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
        url: API_BASE_URL + '/users',
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
