"use strict";

  $('#update-company-status').on('submit', (evt) => {
    evt.preventDefault();

    const companyName = $('#company-name').val();

    $.get('/company_status', {company_name: companyName}, (res) => {
      $('#company-status').text(res);
    });
  });