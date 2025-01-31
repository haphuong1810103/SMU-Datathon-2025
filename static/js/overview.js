// static/js/overview.js

document.addEventListener("DOMContentLoaded", function() {
    // Initialize DataTables for both tables
    $('#pdf-table').DataTable({
        "pageLength": 10, // Show 10 rows per page
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]] // Dropdown for rows per page
    });

    $('#url-table').DataTable({
        "pageLength": 10, // Show 10 rows per page
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]] // Dropdown for rows per page
    });
});