import web
from libraries.utils import hash_utils
from localsys.storage import db


class users_model:
    def get_username(self, user_id):
        """
        Returns username of user given user_id, empty string otherwise.
        """
        users = db.select('users', where="user_id=$user_id", vars=locals())
        if len(users) == 1:
            return users[0].username
        else:
            return ''

    def get_user_id(self, username):
        """
        Returns user_id given username, 0 otherwise.
        """
        users = db.select('users', where="username=$username", vars=locals())
        if len(users) == 1:
            return users[0].user_id
        else:
            return 0

    def authenticate(self, username, password):
        """
        Returns ID of user if successfully authenticated, 0 otherwise.
        """
        password = hash_utils.hash_password(password)
        auth = db.select('users', where="username=$username&&password=$password", vars=locals())
        if len(auth) == 1:
            return auth[0].user_id
        else:
            return 0

    def select_users(self, user_id=0, username=''):
        """
        Returns list of all users with 'username' and 'user_id' (optional) parameters.
        """
        if user_id > 0:
            if username != '':
                return db.select('users', where="username=$username&&user_id=$user_id", vars=locals())
            else:
                return db.select('users', where="user_id=$user_id", vars=locals())
        else:
            return db.select('users', where="username=$username", vars=locals())

    def register(self, username, password, email):
        """
        Attempts to insert new user data into users table.
        Returns ID of user if successfully registered, 0 if user already exists, -1 if database error.
        """
        if len(self.select_users(username=username)) > 0:
            return 0
        else:
            db.insert('users', username=username, email=email, password=hash_utils.hash_password(password))
            user_lookup = self.select_users(username=username)
            if len(user_lookup) == 1:
                return user_lookup[0].user_id
            else:
                return -1

    def update_password(self, user_id, password):
        """
        Updates password according to specified user_id and new password.
        Returns true if updated for one user or password unchanged, false otherwise.
        """
        user_list = self.select_users(user_id=user_id)
        password_hash = hash_utils.hash_password(password)
        if len(user_list) == 1 and password_hash == user_list[0].password:
            return True

        if db.update('users', where="user_id=$user_id", password=password_hash, vars=locals()) \
                == 1:
            return True

        return False

    def request_password(self, token, user_id):
        """
        Creates password recovery ticket in password_recovery table.
        Returns recipient email address if user found, else empty string
        """
        user_list = self.select_users(user_id=user_id)
        if len(user_list) == 1:
            user = user_list[0]
            db.insert('password_recovery', user_id=user.user_id, date=web.SQLLiteral('NOW()'), token=token, invalid=0)
            return user.email
        else:
            return ''

    def password_recovery_user(self, token):
        """
        Return user_id if password request ticket is valid. 0 otherwise.
        :param token:
        """
        user_list = db.select('password_recovery', where="token=$token&&invalid=0", vars=locals())
        if len(user_list) == 1:
            return user_list[0].user_id
        else:
            return 0

    def update_recovery_status(self, token, invalid=1):
        """
        Updates password recovery ticket, assuming successful recovery.
        Returns true if one row affected, else false.
        """
        if db.update('pwrecovery', where="token=$token", invalid=invalid, vars=locals()) == 1:
            return True
        else:
            return False
