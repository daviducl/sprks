__author__ = 'Zhanelya'

import json
import web

from localsys.environment import *

from models.users import users_model
from models.policies import policies_model
from libraries.utils import hash_utils
from models.score import score_model


class account:
    """
    Handles login, and REST API for login/registration.
    """

    def POST(self):
        """
        Authenticates user
        """
        web.header('Content-Type', 'application/json')

        if context.user_id() > 0:
            users_model.session_login(context.user_id())
            return json.dumps(
                {
                    'success': True,
                    'user_id': context.user_id(),
                    'username': context.username(),
                    'messages': ['Successful login']
                }
            )
        else:
            return json.dumps(
                {
                    'success': False,
                    'messages': ['Invalid username/password']
                }
            )

    def PUT(self, username=''):
        """
        Stores user details into database.
        And, if needed, populates tables for first-time user
        """
        payload = json.loads(web.data())
        password = payload.get('password')
        email = payload.get('email')

        web.header('Content-Type', 'application/json')

        if password is None or email is None or username == '' or email == '':
            return json.dumps(
                {
                    'success': False,
                    'messages': ['Username/email/password cannot be empty']
                }
            )

        user_id = users_model().register(username, password, email)

        if user_id == 0:
            return json.dumps(
                {
                    'success': False,
                    'messages': ['User already exists']
                }
            )
        elif user_id > 0:
            if payload.get('autologin', False):
                users_model.session_login(user_id)
            web.ctx.status = '201 Created'
            policies_model.populate_policies(user_id, start_date)
            score_model.insert_score(user_id, 1, 1, start_date)
            score_model.insert_score(user_id, 2, 1, start_date)
            return json.dumps(
                {
                    'success': True,
                    'messages': ['Successfully registered.']
                }
            )
        else:
            return json.dumps(
                {
                    'success': False,
                    'messages': ['Database error']
                }
            )


class password:
    """
    Handles password management
    """

    def PUT(self):
        """
        Changes password for specified user_id
        """

        payload = json.loads(web.data())
        user_model = users_model()

        web.header('Content-Type', 'application/json')

        if context.user_id() > 0:
            user_id = context.user_id()
        else:
            token_user_id = user_model.password_recovery_user(payload.get('token', ''))
            if token_user_id > 0:
                user_id = token_user_id
            else:
                return json.dumps(
                    {
                        'success': False,
                        'messages': ['Unauthorized request']
                    }
                )

        if user_model.update_password(user_id, payload['password']):
            # TODO if token used, invalidate token
            if payload.get('autologin', False) and context.user_id() != user_id:
                # Auto-login user whose password's changed.
                users_model.session_login(user_id)
            return json.dumps(
                {
                    'success': True,
                    'messages': ['Password changed']
                }
            )
        return json.dumps(
            {
                'success': False,
                'messages': ['Database error']
            }
        )

    def POST(self, arg1=0):
        """
        Creates password recovery request, taking argument as user_id (default) or username
        """
        try:
            uid_type = json.loads(web.data()).get('uid_type','')
        except ValueError:
            uid_type = ''

        token = hash_utils.random_hex()

        web.header('Content-Type', 'application/json')

        if uid_type == 'username':
            user_email = users_model().request_password(token, users_model.get_user_id(arg1))
        elif uid_type == 'user_id' or 'uid_type' == '':
            user_email = users_model().request_password(token, int(arg1))
        else:
            return json.dumps(
                {
                    'success': False,
                    'messages': ['Unknown uid type']
                }
            )

        if user_email == '':
            return json.dumps(
                {
                    'success': False,
                    'messages': ['User not found']
                }
            )

        web.config.smtp_server = 'smtp.gmail.com'
        web.config.smtp_port = 587
        web.config.smtp_username = 'sprkssuprt@gmail.com'
        web.config.smtp_password = 'sprks123456789'
        web.config.smtp_starttls = True
        web.sendmail('sprkssuprt@gmail.com', user_email, 'Password recovery',
                     'http://' + web.ctx.host + web.ctx.homepath + '/#password_change_page?token=' + token)
        return json.dumps(
            {
                'success': True,
                'messages': ['Password recovery email sent']
            }
        )