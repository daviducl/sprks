registerModel = {
    username: ko.observable(''),
    password: ko.observable(''),
    passwordConfirm: ko.observable(''),
    email: ko.observable(''),
    messages: ko.observableArray()
};

loginModel = {
    username: ko.observable(''),
    userId: ko.observable(0),
    password: ko.observable(''),
    messages: ko.observableArray()
};

passwordRecoverModel = {
    username: ko.observable(''),
    messages: ko.observableArray()
};

passwordChangeModel = {
    password: ko.observable(''),
    passwordConfirm: ko.observable(''),
    token: ko.observable(''),
    messages: ko.observableArray()
};

$('#registerForm').submit(function (e) {
    e.preventDefault();
    if (registerModel.password() === registerModel.passwordConfirm()) {
        $.ajax({
            type: 'PUT',
            url: 'api/user/account/' + registerModel.username(),
            data: JSON.stringify({
                password: registerModel.password(),
                email: registerModel.email(),
                autologin: true
            }),
            statusCode: {
                500: function () {
                    registerModel.messages(['Server error']);
                },
                200: function (response) {
                    registerModel.messages(response.messages);
                },
                201: function (response) {
                    window.location='/';
                    registerModel.messages(response.messages);
                }
            }
        });
    } else {
        registerModel.messages(["Passwords don't match"]);
    }
});

$('#loginForm').submit(function (e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: 'api/user/account',
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Basic ' + btoa(loginModel.username() + ':' + loginModel.password()));
        },
        statusCode: {
            500: function () {
                loginModel.messages(['Server error']);
            },
            200: function (response) {
                if (response.success === true) {
                    loginModel.username(response.username);
                    loginModel.userId(response.user_id);
                    $('#login_page').hide();
                } else {
                    loginModel.messages(response.messages);
                }
            }
        }
    });
});

$('#passwordRecoveryForm').submit(function (e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: 'api/user/password/' + passwordRecoverModel.username(),
        data: JSON.stringify({
            uid_type: 'username'
        }),
        statusCode: {
            500: function () {
                passwordRecoverModel.messages(['Server error']);
            },
            200: function (response) {
                toastr.info(response.messages[0])
            }
        }
    });
});

$('#passwordChangeForm').submit(function (e) {
    e.preventDefault();
    if (passwordChangeModel.password() === passwordChangeModel.passwordConfirm()) {
        $.ajax({
            type: 'PUT',
            url: 'api/user/password',
            data: JSON.stringify({
                password: passwordChangeModel.password(),
                token: passwordChangeModel.token(),
                autologin: true
            }),
            statusCode: {
                500: function () {
                    toastr.error('Server Error');
                },
                200: function (response) {
                    toastr.success(response.messages[0]);
                    if (response.success === true) {
                        console.log('changed pswd successfully');
                        passwordChangeModel.password('');
                        passwordChangeModel.passwordConfirm('');
                    }
                }
            }
        });
    } else {
        passwordChangeModel.messages(["Passwords don't match"]);
    }
});

$('#logout-link').click(function(){
    loginModel.username('');
    loginModel.userId('');
    loginModel.password('');
    toastr.info('Logging out...');
    $.ajax({
        type: 'GET',
        url: '/?action=logout',
        statusCode: {
            200: function () {
                    loginModel.username('');
                    loginModel.userId(0);
                }
            }
    });
});

function check_loggedin() {
    $.ajax({
        type: 'POST',
        url: 'api/user/account',
        statusCode: {
            200: function (response) {
                toastr.clear();
                if (response.success === true) {
                    loginModel.username(response.username);
                    loginModel.userId(response.user_id);
                } else {
                    loginModel.username('');
                    loginModel.userId(0);
                }
            }
        }
    });
}

$(function () {

    $("#home_page").show();
    toastr.info('Loading...');

    ko.applyBindings(registerModel, document.getElementById('registerForm'));
    ko.applyBindings(loginModel, document.getElementById('loginForm'));
    ko.applyBindings(passwordRecoverModel, document.getElementById('passwordRecoveryForm'));
    ko.applyBindings(passwordChangeModel, document.getElementById('passwordChangeForm'));

    loginModel.userId.subscribe(function (userId) {
        toastr.clear();
        if (userId > 0) {
            toastr.info('Logged in.');
            resume();
            retrieve_scores();
            $('#controls').show();
            $('#logout-link').show();
            $('#login-link').hide();
            $('span.username').text(loginModel.username());
            $("#home_page").hide();
            $("#intro_page").show();
            highlightActiveButton();
            get_score_frame();
        } else {
            toastr.info('Logged out.');
            $('#controls').hide();
            $('#logout-link').hide();
            $('#login-link').show();
            $('span.username').text('');
            $("#home_page").show();
            $("#intro_page").hide();
        }
    });

    if ($.url('?token') != null) {
        passwordChangeModel.token($.url('?token'));
        // Cleans URL parameters
        history.pushState({},'title', '/');
        $("#home_page").hide();
        $("#password_change_page").show();
    }

    check_loggedin();

});