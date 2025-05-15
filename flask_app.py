import os
from datetime import datetime

from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from sqlalchemy import desc

from data import db_session
from data.api import users_resources, videos_resources, comments_resources
from data.users import User, followers
from data.video import Video
from data.comments import Comment

from pyffmpeg import FFmpeg

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'
login_manager.login_message_category = "info"
login_manager.login_message = "Пожалуйста, войдите в аккаунт."


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html', title='Не найдено', error_text='Страница не найдена', e=e)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    videos = db_sess.query(Video).filter(Video.is_private == False).order_by(desc(Video.id))

    return render_template('index.html', title='VsratTube', videos=videos)


@app.route('/search', methods=['GET'])
def search():
    searched = request.args.get('q')
    if searched:
        db_sess = db_session.create_session()
        channels = db_sess.query(User).filter(User.username.ilike(f'%{searched}%')).all()
        videos = db_sess.query(Video).filter(
            Video.is_private == False,
            Video.title.ilike(f'%{searched}%')
        ).all()
        return render_template('search.html', search_str=searched, title=searched,
                               channels=channels, videos=videos)
    return redirect("/")


@app.route('/video/<int:id_video>')
def video(id_video):
    db_sess = db_session.create_session()
    video = db_sess.query(Video).get(id_video)
    c_user = db_sess.query(User).get(current_user.id) if current_user.is_authenticated else None
    videos_last = db_sess.query(Video).filter(Video.is_private == False).order_by(desc(Video.id))

    if video and (video.is_private == False or (video.is_private == True and c_user == video.author)):
        return render_template('video.html', title=video.title, video=video, current_user=c_user,
                               user=video.author, videos_last=videos_last)
    else:
        return render_template('not_found.html', title='Не найдено', error_text='Видео не найдено')


@app.route('/video/')
@app.route('/video')
@app.route('/channel')
@app.route('/channel/')
def page_empty():
    return redirect(url_for('index'))


@app.route('/channel/<int:id_user>')
def channel(id_user):
    db_sess = db_session.create_session()
    u = db_sess.query(User).get(id_user)
    if u:
        c_user = db_sess.query(User).get(current_user.id) if current_user.is_authenticated else None
        videos = u.videos.filter(Video.is_private == False).order_by(
            desc(Video.id)) if u != c_user else u.videos.order_by(desc(Video.id))
        return render_template('channel.html', videos=videos, followers=followers, title=u.username, user=u,
                               current_user=c_user)
    else:
        return render_template('not_found.html', title='Не найдено', error_text='Канал не найден')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        video_file = request.files['video']
        preview_file = request.files.get('preview')
        is_private = request.form.getlist('is_private')

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)

        if video_file:
            video_filename = f"video_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
            video_path = os.path.join(f"{app.config['UPLOAD_FOLDER']}/videos", video_filename)
            video_file.save(video_path)

            preview_filename = f"preview_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            preview_path = os.path.join(f"{app.config['UPLOAD_FOLDER']}/previews", preview_filename)
            if preview_file:
                preview_file.save(preview_path)
            else:
                ff = FFmpeg()
                ff.options(f'-i {video_path} -vframes 1 {preview_path}')

            user.videos.append(
                Video(video_path=f'/{video_path}', preview=f'/{preview_path}', title=title, description=description,
                      is_private=bool(is_private), author_id=current_user.id))

            db_sess.commit()
            flash('Видео успешно загружено!', 'success')
            return redirect(url_for('channel', id_user=current_user.id))

    return render_template('upload.html', title='Загрузка видео')


@app.route('/followed')
@login_required
def followed():
    users = current_user.followed.all()

    return render_template('followed.html', title="Мои подписки", users=users)


@app.route('/liked')
@login_required
def liked():
    videos = current_user.liked.filter(Video.is_private == False)

    return render_template('liked.html', title="Понравившиеся видео", current_user=current_user, videos=videos)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_data = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('rememberMe')

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter((User.email == login_data) | (User.username == login_data)).first()

        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for(f'channel', id_user=current_user.id))
        else:
            flash('Неверный email/имя пользователя или пароль', 'danger')

    return redirect(url_for('index'))


@app.route('/edit_password', methods=['POST'])
@login_required
def edit_password():
    old_password = request.form.get('oldPassword')
    new_password = request.form.get('newPassword')
    new_password_again = request.form.get('newPasswordAgain')

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)

    if user.check_password(old_password):
        if new_password == new_password_again:
            user.set_password(new_password)
            flash('Пароль сменён', 'success')
        else:
            flash('Пароли не совпадают', 'danger')
    else:
        flash('Неверно введён старый пароль', 'danger')

    db_sess.commit()
    return redirect(url_for('channel', id_user=current_user.id))


@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    email = request.form.get('editEmail')
    username = request.form.get('editUsername')
    avatar = request.files.get('editAvatar')

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)

    user.email = email
    user.username = username

    if avatar:
        img = Image.open(avatar.stream)
        width, height = img.size
        if width > height or width == height:
            wpercent = (250 / float(height))
            wsize = int((float(width) * float(wpercent)))
            img = img.resize((wsize, 250))
        else:
            wpercent = (250 / float(width))
            hsize = int((float(height) * float(wpercent)))
            img = img.resize((250, hsize))
        width, height = img.size
        left = (width - 250) / 2
        top = (height - 250) / 2
        right = (width + 250) / 2
        bottom = (height + 250) / 2
        img = img.crop((left, top, right, bottom))

        avatar_filename = f"avatar_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        avatar_path = os.path.join(f"{app.config['UPLOAD_FOLDER']}/avatars", avatar_filename)
        img.save(avatar_path)
        user.avatar = f"/{avatar_path}"

    db_sess.commit()

    flash('Профиль изменен', 'success')
    return redirect(url_for('channel', id_user=current_user.id))


@app.route('/delete_avatar')
@login_required
def delete_avatar():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)

    user.avatar = '/static/img/no_avatar.jpeg'
    db_sess.commit()

    flash('Аватарка удалена', 'success')
    return redirect(url_for('channel', id_user=current_user.id))


@app.route('/delete_preview', methods=['POST'])
@login_required
def delete_preview():
    db_sess = db_session.create_session()
    video_id = request.form.get('video_id')
    video_edit = db_sess.query(Video).filter(Video.author == current_user, Video.id == video_id).first()

    preview_filename = f"preview_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    preview_path = os.path.join(f"{app.config['UPLOAD_FOLDER']}/previews", preview_filename)
    ff = FFmpeg()
    ff.options(f'-i {video_edit.video_path[1:]} -vframes 1 {preview_path}')
    video_edit.preview = f'/{preview_path}'
    db_sess.commit()

    flash('Превью удален', 'success')
    return redirect(url_for('video', id_video=video_edit.id))


@app.route('/edit_video', methods=['POST'])
@login_required
def edit_video():
    db_sess = db_session.create_session()
    video_id = request.form.get('video_id')
    title = request.form.get('editTitle')
    description = request.form.get('editDescription')
    preview_file = request.files.get('editPreview')
    is_private = request.form.getlist('editIs_private')
    video_edit = db_sess.query(Video).filter(Video.author == current_user, Video.id == video_id).first()

    preview_filename = f"preview_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    preview_path = os.path.join(f"{app.config['UPLOAD_FOLDER']}/previews", preview_filename)
    if preview_file:
        preview_file.save(preview_path)
        video_edit.preview = f'/{preview_path}'

    video_edit.title = title
    video_edit.description = description
    video_edit.is_private = bool(is_private)

    db_sess.commit()

    flash('Видео изменено', 'success')
    return redirect(url_for('video', id_video=video_edit.id))


@app.route('/delete_video', methods=['POST'])
@login_required
def delete_video():
    db_sess = db_session.create_session()
    video_id = request.form.get('video_id')
    video_delete = db_sess.query(Video).filter(Video.author == current_user, Video.id == video_id).first()

    db_sess.delete(video_delete)
    db_sess.commit()

    flash('Видео удалено', 'success')
    return redirect(url_for('channel', id_user=current_user.id))


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash('Пароли не совпадают', 'danger')
        return redirect(url_for('index'))

    db_sess = db_session.create_session()
    if db_sess.query(User).filter(User.email == email).first():
        flash('Пользователь с такой почтой уже существует', 'danger')
        return redirect(url_for('index'))
    elif db_sess.query(User).filter(User.username == username).first():
        flash('Пользователь с таким именем пользователя уже существует', 'danger')
        return redirect(url_for('index'))

    new_user = User(username=username, email=email, avatar='/static/img/no_avatar.jpeg')

    new_user.set_password(password)
    db_sess.add(new_user)
    db_sess.commit()
    login_user(new_user)
    flash('Регистрация прошла успешно!', 'success')
    return redirect(url_for(f'channel', id_user=new_user.id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


def main():
    db_session.global_init("db/vt_main.sql")
    api.add_resource(users_resources.UserResource, '/api/users/<int:user_id>')
    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(users_resources.UserFollowedResource, '/api/users/<int:user_id>/followed')
    api.add_resource(users_resources.UserFollowersResource, '/api/users/<int:user_id>/followers')
    api.add_resource(users_resources.UserFollowResource, '/api/users/<int:user_id>/follow')
    api.add_resource(users_resources.UserUnfollowResource, '/api/users/<int:user_id>/unfollow')
    api.add_resource(users_resources.UserAvatarDeleteResource, '/api/users/avatar_delete')
    api.add_resource(users_resources.UserChangePasswordResource, '/api/users/change_password')
    api.add_resource(videos_resources.VideoLikeResource, '/api/videos/<int:video_id>/like')
    api.add_resource(videos_resources.VideoUnlikeResource, '/api/videos/<int:video_id>/unlike')
    api.add_resource(videos_resources.VideoResource, '/api/videos/<int:video_id>')
    api.add_resource(videos_resources.VideosListResource, '/api/videos')
    api.add_resource(comments_resources.CommentVideoResource, '/api/comment')

    if not os.path.exists(f"{app.config['UPLOAD_FOLDER']}/avatars"):
        os.makedirs(f"{app.config['UPLOAD_FOLDER']}/avatars")
    if not os.path.exists(f"{app.config['UPLOAD_FOLDER']}/previews"):
        os.makedirs(f"{app.config['UPLOAD_FOLDER']}/previews")
    if not os.path.exists(f"{app.config['UPLOAD_FOLDER']}/videos"):
        os.makedirs(f"{app.config['UPLOAD_FOLDER']}/videos")
    if not os.path.exists("/db"):
        os.makedirs("/db")

    app.run()


if __name__ == '__main__':
    main()
