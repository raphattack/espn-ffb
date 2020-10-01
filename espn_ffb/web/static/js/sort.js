$(document).ready(function() {
    var table = $('table.table').DataTable( {
        paging: false,
        searching: false,
        info: false
        // buttons: {
        //     buttons: [
        //         { extend: 'copy', className: 'btn-outline-secondary btn-sm ml-2' },
        //         { extend: 'excel', className: 'btn-outline-secondary btn-sm' },
        //         { extend: 'pdf', className: 'btn-outline-secondary btn-sm' },
        //         { extend: 'csv', className: 'btn-outline-secondary btn-sm' },
        //         { extend: 'print', className: 'btn-outline-secondary btn-sm' },
        //         { extend: 'colvis', className: 'btn-outline-secondary btn-sm' }
        //     ],
        //     dom: { button: { className: 'btn' } }
        // }
    } );
    table.buttons().container().appendTo('.dataTables_wrapper .col-md-6:eq(0)');
} );