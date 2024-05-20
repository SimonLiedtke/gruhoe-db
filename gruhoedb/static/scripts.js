$(document).ready(function () {
    new DataTable('#searchResults', {
        "searching": false,
        "lengthChange": false,
        "order": [[0, 'desc']]
    });

    const picksToSyncTable = new DataTable('#pickstosync', {
        "searching": false,
        "lengthChange": false,
        "order": [[0, 'desc']]
    });

    const loginDialog = $("#login-dialog").dialog({
        autoOpen: false,
        buttons: {
            Login: login,
            Cancel: function() {
                loginDialog.dialog("close");
            }
        }
    });

    $("#login").on("click", function() {
        loginDialog.dialog("open");
    });

    function login() {
        const passwordField = $("#password");
        const data = new FormData();
        data.append("password", passwordField.val());
        fetch("/login", {
            "method": "POST",
            "body": data,
        }).then((response) => {
            if (response.ok) {
                passwordField.removeClass("ui-state-error");
                loginDialog.dialog("close");
                syncDialog.dialog("open");
            } else {
                passwordField.addClass("ui-state-error");
            }
        });

    }

    const syncDialog = $("#sync-dialog").dialog({
        autoOpen: false,
        buttons: {
            "Get list of new picks": getNewPicks,
            "Sync from Google docs to GruHö DB": sync,
        },
        width: 800
    });

    function getNewPicks() {
        fetch("/newpicks")
            .then((response) => response.json())
            .then((picks) => {
                if (picks) {
                    picksToSyncTable.clear();
                }

                let date, artist, album;
                picks.forEach(pick => {
                    date = new Date(pick[0], pick[1]-1, pick[2]).toLocaleDateString();
                    artist = pick[3];
                    album = pick[4];
                    picksToSyncTable.row.add([date, artist, album])
                });

                picksToSyncTable.draw();
            })
            .catch(console.error);
    }

    function sync() {
        fetch("/sync", {
            "method": "POST",
        }).then((response) => {
            console.log(response);
        });
    }
});