// ============================
// >> WELCOME PAGE
// ============================


var guildStatusRank = {
    'currentMember': 1,
    'exMember': 2,
    'other': 3,
    '': 3,
}

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
            var rawUsersData = JSON.parse(response);
            var preUsers = rawUsersData.filter(
                function(u) {
                    return !!u.preRegistration;
                }
            );
            var preUsers = preUsers.sort(
                function(a, b) {
                    return a.timestamp - b.timestamp;
                }
            );

            var regularUsers = rawUsersData.filter(
                function(u) {
                    return !u.preRegistration;
                }
            );
            var regularUsers = regularUsers.sort(
                function(a, b) {
                    var aRank = guildStatusRank[a.guildStatus];
                    var bRank = guildStatusRank[b.guildStatus];
                    if (aRank !== bRank) {
                        return aRank - bRank;
                    } else {
                        return a.timestamp - b.timestamp;
                    }
                }
            );
            var usersData = preUsers.concat(regularUsers);

            var priorityUsers = usersData.filter(
                function(u) {
                    return !!u.preRegistration || u.guildStatus === 'currentMember';
                }
            );
            if (priorityUsers.length < 452) {
                $('#registrationButtonContainer').removeClass('hidden');
            }
            for (var i = 0; i < usersData.length; i++) {
                insertUserToTable(i + 1, table, usersData[i]);
            }
       
        },
        error: function(response) {
            console.error('ERROR', response);
   
        },
    });
});
