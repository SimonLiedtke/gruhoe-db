$(document).ready(function () {
    $('#searchResults').DataTable({
        "searching": false,
        "lengthChange": false,
        "order": [[0, 'desc']]
    });
});