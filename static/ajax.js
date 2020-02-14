"use strict";

      $('#heart').on('submit', (evt) => {
        evt.preventDefault();

        const selectedId = $('#human-id').val();
        const url = '/api/human/' + selectedId

        // alert(selectedId);

         $.get(url, (res) => {
           $('#fname').html(res.fname),
           $('#lname').html(res.lname),
           $('#email').html(res.email);
         });

     });