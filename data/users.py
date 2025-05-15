import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase

followers = Table(
    'followers', SqlAlchemyBase.metadata,
    Column('follower_id', Integer, ForeignKey('users.id')),
    Column('followed_id', Integer, ForeignKey('users.id'))
)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    avatar = sqlalchemy.Column(sqlalchemy.String, default='/static/img/no_avatar.jpeg')
    followed = relationship(
        'User', secondary=followers,
        primaryjoin=(id == followers.c.follower_id),
        secondaryjoin=(id == followers.c.followed_id),
        backref=backref('followers', lazy='dynamic'), lazy='dynamic')

    videos = relationship("Video", back_populates='author', lazy='dynamic')
    comments = relationship("Comment", back_populates='author')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def follow(self, user):
        if not self.is_following(user) and self.id != user.id:
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def __repr__(self):
        return (f"<User> {self.id} {self.username} {self.email} {self.hashed_password} {self.avatar}")
