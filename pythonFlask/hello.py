import math
import time

from flask import Flask, render_template                         , g, request, flash, abort
import psycopg2

# конфигурация
DATABASE = "library"
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
USERNAME = "postgres"
PASSWORD = "root"
HOST = "localhost"

app = Flask(__name__)
app.secret_key = SECRET_KEY


def connect_db():
    conn = psycopg2.connect(dbname=DATABASE, user=USERNAME,
                            password=PASSWORD, host=HOST)
    return conn


menu = ["Установка", "Первое приложение", "Обратная связь"]


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


# @app.route("/index")
# @app.route("/")
# def index():
#     db = get_db()
#     return render_template('index.html', menu=[])


@app.route("/about")
def about():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('about.html', title="О сайте", menu=dbase.getMenu())


def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


# def create_db():
#     """Вспомогательная функция для создания таблиц БД"""
#     db = connect_db()
#     with app.open_resource('sq_db.sql', mode='r') as f:
#         db.cursor().executescript(f.read())
#     db.commit()
#     db.close()


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            print(res)
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addPost(self, title, text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts ( title, text, time) "
                               "VALUES( %s, %s, %s)", [title, text, tm])
            self.__db.commit()
        except psycopg2.Error as e:
            print("Ошибка добавления статьи в БД " + str(e))
            return False
        return True

    def getPost(self, postId):
        try:
            self.__cur.execute("SELECT title, text FROM posts  "
                               "WHERE id = %s LIMIT 1", [postId])
            res = self.__cur.fetchone()
            if res:
                return res
        except psycopg2.Error as e:
            print("Ошибка получения статьи из БД " + str(e))
        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except psycopg2.Error as e:
            print("Ошибка получения статьи из БД " + str(e))
        return []


@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")


@app.route("/post/<int:id_post>")
def showPost(id_post):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(id_post)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


if __name__ == "__main__":
    app.run(debug=True)
