from flask import jsonify
from flask_login import current_user
from flask_restful import Resource, abort

from data import db_session
from data.video import Video


def abort_if_video_not_found(video_id):
    session = db_session.create_session()
    user = session.query(Video).get(video_id)
    if not user:
        abort(404, message=f"User {video_id} not found")

class VideoUnlikeResource(Resource):
    def get(self, video_id):
        abort_if_video_not_found(video_id)
        db_sess = db_session.create_session()
        video = db_sess.query(Video).get(video_id)
        current = db_sess.merge(current_user)
        if video.is_liked(current):
            video.unlike(current)
            db_sess.commit()
            return jsonify({'success': 'OK'})
        else:
            abort(400, message=f"Already unliked")


class VideoLikeResource(Resource):
    def get(self, video_id):
        abort_if_video_not_found(video_id)
        db_sess = db_session.create_session()
        video = db_sess.query(Video).get(video_id)
        current = db_sess.merge(current_user)
        if not video.is_liked(current):
            video.like(current)
            db_sess.commit()
            return jsonify({'success': 'OK'})
        else:
            abort(400, message=f"Already liked")
