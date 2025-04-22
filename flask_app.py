from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def index():
    return render_template('index.html', title='VsratTube')


@app.route('/search', methods=['GET'])
def search():
    searched = request.args.get('q')
    if searched:
        return render_template('search.html', search_str=searched, title=searched)
    return redirect("/ ")


if __name__ == '__main__':
    app.run()
