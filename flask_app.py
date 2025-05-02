from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Конфигурация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Модель пользователя
class User(UserMixin):
    def __init__(self, id, username, email, password, avatar=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.avatar = avatar
        self.videos = []

    def get_id(self):
        return str(self.id)


# Простая "база данных" для демонстрации
users_db = {
    1: User(1, 'admin', 'admin@example.com', generate_password_hash('password'), '/static/img/no_avatar.jpeg')
}


# Загрузчик пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return users_db.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html', title='VsratTube')


@app.route('/search', methods=['GET'])
def search():
    searched = request.args.get('q')
    if searched:
        return render_template('search.html', search_str=searched, title=searched)
    return redirect("/")


@app.route('/channel')
def channel():
    return render_template('channel.html', title='ChannelName')


@app.route('/video')
def video():
    return render_template('video.html', title='VideoName')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Профиль', user=current_user)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        video_file = request.files['video']
        preview_file = request.files.get('preview')

        if video_file:
            # Сохранение видео
            video_filename = f"video_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            video_file.save(video_path)

            # Сохранение превью, если есть
            preview_path = None
            if preview_file:
                preview_filename = f"preview_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                preview_path = os.path.join(app.config['UPLOAD_FOLDER'], preview_filename)
                preview_file.save(preview_path)

            # Добавление видео к пользователю
            current_user.videos.append({
                'title': title,
                'description': description,
                'video_path': '/' + video_path,
                'preview': '/' + preview_path if preview_path else '/static/img/preview.png',
                'views': 0,
                'upload_date': datetime.now().strftime('%d.%m.%Y')
            })

            flash('Видео успешно загружено!', 'success')
            return redirect(url_for('profile'))

    return render_template('upload.html', title='Загрузка видео')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_data = request.form.get('login')
        password = request.form.get('password')

        # Поиск пользователя
        user = None
        for u in users_db.values():
            if u.email == login_data or u.username == login_data:
                user = u
                break

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Неверный email/имя пользователя или пароль', 'danger')

    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash('Пароли не совпадают', 'danger')
        return redirect(url_for('index'))

    # Проверка существования пользователя
    for u in users_db.values():
        if u.email == email or u.username == username:
            flash('Пользователь с таким email или именем уже существует', 'danger')
            return redirect(url_for('index'))

    # Создание нового пользователя
    new_id = max(users_db.keys()) + 1
    new_user = User(new_id, username, email, generate_password_hash(password))
    users_db[new_id] = new_user

    login_user(new_user)
    flash('Регистрация прошла успешно!', 'success')
    return redirect(url_for('profile'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Создаем папку для загрузок, если ее нет
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)