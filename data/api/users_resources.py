from flask import jsonify
from flask_login import current_user
from flask_restful import Resource, reqparse, abort
from data import db_session
from data.users import User


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


parser_usersChangePassword = reqparse.RequestParser()
parser_usersChangePassword.add_argument('old_password', required=True)
parser_usersChangePassword.add_argument('new_password', required=True)
parser_usersChangePassword.add_argument('new_password_again', required=True)


class UserChangePasswordResource(Resource):
    def post(self):
        args = parser_usersChangePassword.parse_args()

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)

        if user.check_password(args['old_password']):
            if args['new_password'] == args['new_password_again']:
                user.set_password(args['new_password'])
                db_sess.commit()
                return jsonify({'success': 'OK'})
            else:
                abort(400, message=f"The passwords do not match ")
        else:
            abort(400, message=f"The old password is not correct")


class UserAvatarDeleteResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        current = db_sess.merge(current_user)
        current.avatar = '/static/img/no_avatar.jpeg'
        db_sess.commit()

        return jsonify({'success': 'OK'})


class UserUnfollowResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        current = db_sess.merge(current_user)
        if current.is_following(user):
            current.unfollow(user)
            db_sess.commit()
            return jsonify({'success': 'OK'})
        else:
            abort(400, message=f"Already unfollowed")


class UserFollowResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        current = db_sess.merge(current_user)
        if not current.is_following(user):
            if user != current:
                current.follow(user)
                db_sess.commit()
                return jsonify({'success': 'OK'})
            else:
                abort(400, message=f"Can't follow yourself")
        else:
            abort(400, message=f"Already followed")


class UserFollowedResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        users = user.followed.all()
        return jsonify(
            {
                'users':
                    [item.to_dict(only=('id', 'username', 'email', 'avatar')) for item in users]
            }
        )


class UserFollowersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        users = user.followers.all()
        return jsonify(
            {
                'users':
                    [item.to_dict(only=('id', 'username', 'email', 'avatar')) for item in users]
            }
        )


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': [user.to_dict(only=('id', 'username', 'email', 'avatar'))]})


parser_usersList = reqparse.RequestParser()
parser_usersList.add_argument('username', required=True)
parser_usersList.add_argument('email', required=True)
parser_usersList.add_argument('password', required=True)


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify(
            {
                'users':
                    [item.to_dict(only=('id', 'username', 'email', 'avatar')) for item in users]
            }
        )

    def post(self):
        args = parser_usersList.parse_args()
        session = db_session.create_session()
        user = User(
            username=args['username'],
            email=args['email'])
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})
