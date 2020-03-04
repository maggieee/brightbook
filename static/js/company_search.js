"use strict";

$(document).ready(function() {
    $('.company-search').select2();
});


$('#company-search').on('submit', (evt) => {
    evt.preventDefault();

    const companyName = $('#company-search').val();

    $.get('/company_search', {company_name: companyName}, (res) => {
      $('#company-search-result').html(res);
    });
  });