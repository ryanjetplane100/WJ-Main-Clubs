# user.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)

    @classmethod
    def from_password_hash(cls, id, username, password_hash):
        user = cls.__new__(cls)
        user.id = id
        user.username = username
        user.password_hash = password_hash
        return user

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
