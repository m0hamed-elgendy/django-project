/**
 * script.js — Client-side JavaScript for the Crowdfunding Platform.
 *
 * Handles:
 * - Flash message auto-dismiss and close buttons
 * - Mobile navbar toggle
 * - Client-side form validation (email, phone, password match, etc.)
 */

document.addEventListener('DOMContentLoaded', function () {

    // ----------------------------------------------------------------
    //  Flash message close buttons & auto-dismiss
    // ----------------------------------------------------------------
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(function (msg) {
        // Close button
        const closeBtn = msg.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                msg.style.animation = 'slideUp 0.3s ease-out forwards';
                setTimeout(function () { msg.remove(); }, 300);
            });
        }

        // Auto-dismiss after 6 seconds
        setTimeout(function () {
            if (msg.parentNode) {
                msg.style.animation = 'slideUp 0.3s ease-out forwards';
                setTimeout(function () { msg.remove(); }, 300);
            }
        }, 6000);
    });

    // Add slideUp animation
    const style = document.createElement('style');
    style.textContent = '@keyframes slideUp { from { opacity: 1; transform: translateY(0); } to { opacity: 0; transform: translateY(-10px); } }';
    document.head.appendChild(style);


    // ----------------------------------------------------------------
    //  Mobile navbar toggle
    // ----------------------------------------------------------------
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('active');
        });

        // Close menu when clicking a link
        navLinks.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.classList.remove('active');
            });
        });
    }


    // ----------------------------------------------------------------
    //  Client-side form validation helpers
    // ----------------------------------------------------------------
    function showFieldError(field, message) {
        clearFieldError(field);
        field.parentElement.classList.add('has-error');
        var errorSpan = document.createElement('span');
        errorSpan.className = 'field-error';
        errorSpan.textContent = message;
        field.parentElement.appendChild(errorSpan);
    }

    function clearFieldError(field) {
        field.parentElement.classList.remove('has-error');
        var existing = field.parentElement.querySelector('.field-error');
        if (existing) {
            existing.remove();
        }
    }

    function clearAllErrors(form) {
        form.querySelectorAll('.has-error').forEach(function (el) {
            el.classList.remove('has-error');
        });
        form.querySelectorAll('.field-error').forEach(function (el) {
            el.remove();
        });
    }

    // Email regex
    var emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    // Egyptian phone regex
    var phoneRegex = /^01[0125]\d{8}$/;


    // ----------------------------------------------------------------
    //  Registration form validation
    // ----------------------------------------------------------------
    var registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
            clearAllErrors(registerForm);
            var valid = true;

            var firstName = document.getElementById('first_name');
            var lastName = document.getElementById('last_name');
            var email = document.getElementById('email');
            var password = document.getElementById('password');
            var confirmPassword = document.getElementById('confirm_password');
            var phone = document.getElementById('phone');

            if (!firstName.value.trim()) {
                showFieldError(firstName, 'First name cannot be empty.');
                valid = false;
            }

            if (!lastName.value.trim()) {
                showFieldError(lastName, 'Last name cannot be empty.');
                valid = false;
            }

            if (!email.value.trim()) {
                showFieldError(email, 'Email cannot be empty.');
                valid = false;
            } else if (!emailRegex.test(email.value.trim())) {
                showFieldError(email, 'Invalid email format.');
                valid = false;
            }

            if (!password.value) {
                showFieldError(password, 'Password cannot be empty.');
                valid = false;
            } else if (password.value.length < 6) {
                showFieldError(password, 'Password must be at least 6 characters.');
                valid = false;
            }

            if (!confirmPassword.value) {
                showFieldError(confirmPassword, 'Please confirm your password.');
                valid = false;
            } else if (password.value !== confirmPassword.value) {
                showFieldError(confirmPassword, 'Passwords do not match.');
                valid = false;
            }

            if (!phone.value.trim()) {
                showFieldError(phone, 'Phone number cannot be empty.');
                valid = false;
            } else if (!phoneRegex.test(phone.value.trim())) {
                showFieldError(phone, 'Invalid Egyptian phone number (010/011/012/015, 11 digits).');
                valid = false;
            }

            if (!valid) {
                e.preventDefault();
            }
        });
    }


    // ----------------------------------------------------------------
    //  Project form validation (create & edit)
    // ----------------------------------------------------------------
    var projectForms = document.querySelectorAll('#project-create-form, #project-edit-form');
    projectForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            clearAllErrors(form);
            var valid = true;

            var title = form.querySelector('#title');
            var details = form.querySelector('#details');
            var totalTarget = form.querySelector('#total_target');
            var startDate = form.querySelector('#start_date');
            var endDate = form.querySelector('#end_date');

            if (!title.value.trim()) {
                showFieldError(title, 'Title cannot be empty.');
                valid = false;
            }

            if (!details.value.trim()) {
                showFieldError(details, 'Details cannot be empty.');
                valid = false;
            }

            if (!totalTarget.value) {
                showFieldError(totalTarget, 'Target amount is required.');
                valid = false;
            } else if (parseFloat(totalTarget.value) <= 0 || isNaN(parseFloat(totalTarget.value))) {
                showFieldError(totalTarget, 'Target must be a positive number.');
                valid = false;
            }

            if (!startDate.value) {
                showFieldError(startDate, 'Start date is required.');
                valid = false;
            }

            if (!endDate.value) {
                showFieldError(endDate, 'End date is required.');
                valid = false;
            }

            if (startDate.value && endDate.value) {
                if (new Date(endDate.value) <= new Date(startDate.value)) {
                    showFieldError(endDate, 'End date must be after the start date.');
                    valid = false;
                }
            }

            if (!valid) {
                e.preventDefault();
            }
        });
    });


    // ----------------------------------------------------------------
    //  Search form — ensure at least start date is provided
    // ----------------------------------------------------------------
    var searchForm = document.getElementById('project-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            clearAllErrors(searchForm);
            var startDate = searchForm.querySelector('#start_date');

            if (!startDate.value) {
                showFieldError(startDate, 'Please select a start date.');
                e.preventDefault();
            }
        });
    }

});
