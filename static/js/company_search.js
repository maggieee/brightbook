"use strict";

$(document).ready(function() {
    $('.company-search').select2();
});

$('#company-search-form').on('submit', (evt) => {
    evt.preventDefault();

    const companyName = $('#company-search').val();

    $.get('/company_search', {company_name: companyName}, (res) => {
        console.log(res)
      $('#company-has-hired-hackbrighters').html(res.company_name +" has hired a Hackbrighter as her first SWE job.");
      // $('#company-job-listings').html("You can find " +res.company_name +"'s job listings at" + "<a href='"+res.job_listings_link+"'. /a>");
      $('#company-job-listings').load('/companies/'+res.company_id)
    });
  });
 