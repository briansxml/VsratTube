from flask import jsonify
from flask_login import current_user
from flask_restful import Resource, reqparse, abort

from data import db_session
from data.video import Video

parser_CommentVideo = reqparse.RequestParser()
parser_CommentVideo.add_argument('video_id', required=True)
parser_CommentVideo.add_argument('text', required=True)


def abort_if_user_not_authorized():
    session = db_session.create_session()
    user = session.merge(current_user) if current_user.is_authenticated else None
    if not user:
        abort(401, message=f"Unauthorized")


def abort_if_video_not_found(video_id):
    session = db_session.create_session()
    user = session.query(Video).get(video_id)
    if not user:
        abort(404, message=f"Video {video_id} not found")


class CommentVideoResource(Resource):
    def post(self):
        args = parser_CommentVideo.parse_args()
        video_id = args['video_id']
        abort_if_video_not_found(video_id)
        abort_if_user_not_authorized()
        db_sess = db_session.create_session()
        current = db_sess.merge(current_user)
        video = db_sess.query(Video).get(video_id)
        video.comment(current, args['text'])
        db_sess.commit()
        return jsonify({'success': 'OK'})
