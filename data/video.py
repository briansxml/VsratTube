import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase
from data.users import User

likes = Table(
    'likes', SqlAlchemyBase.metadata,
    Column('liker_id', Integer, ForeignKey('users.id')),
    Column('liked_id', Integer, ForeignKey('videos.id'))
)


class Video(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'videos'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    author = relationship("User")
    video_path = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    preview = sqlalchemy.Column(sqlalchemy.String)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    likers = relationship(
        "User", secondary=likes, primaryjoin=(id == likes.c.liked_id),
        secondaryjoin=(User.id == likes.c.liker_id), backref=backref('liked', lazy='dynamic'), lazy='dynamic')

    # comments = relationship("Comment", back_populates='video')

    def like(self, user):
        if not self.is_liked(user):
            self.likers.append(user)

    def unlike(self, user):
        if self.is_liked(user):
            self.likers.remove(user)

    def is_liked(self, user):
        return self.likers.filter(
            likes.c.liker_id == user.id).count() > 0

    def __repr__(self):
        return (
            f"<Video> {self.id} {self.author_id} {self.video_path} {self.title} {self.description} {self.preview} {self.is_private}")
