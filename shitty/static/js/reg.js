/*global $, console*/

$(function () {

    'use strict';

    ////// page side animation

    $('.login-section').on('click', function () {
            window.location = "/driver/"
    });

    $('.loggin-section').on('click', function () {
            window.location = "/biogas/"
    });

    $('.signup-section').on('click', function () {
            window.location = "/user/"
    });

    ////// custom placeholder

    $('.login-page_input').on('change', function () {
        var input = $(this);
        if (input.val().length) {
            input.addClass('hide-placeholder');
        } else {
            input.removeClass('hide-placeholder');
        }
    });

    //// forget password

    $('.login-page_forget a').on('click', function (e) {
        e.preventDefault();
        $('.login-form').slideUp();
        $('.forget-form').slideDown();
    });
});
