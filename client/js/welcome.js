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
    cellName.innerHTML = user.name.substring(0, 36);
    cellName.style.wordBreak = 'break-word';
    cellTable.innerHTML = user.table.substring(0, 36);
    cellTable.style.wordBreak = 'break-all';
}

// On page load get users and insert them to table
$(function() {
    var table = document.getElementById('registeredUsers');
    $.ajax({
        url: API_BASE_URL + '/users',
        type: "GET",
        success: function(response) {
            var usersData = JSON.parse(response);
            var usersData = usersData.sort(
                function(a, b) {
                    return a.timestamp - b.timestamp;
                }
            );
            // if (usersData.length < 250) {
            //     $('#registrationButtonContainer').removeClass('hidden');
            // }
            for (var i = 0; i < usersData.length; i++) {
                insertUserToTable(i + 1, table, usersData[i]);
            }
       
        },
        error: function(response) {
            console.error('ERROR', response);
   
        },
    });
});
