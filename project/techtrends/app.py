import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from logging.config import dictConfig

class DBFactory():
    __db_connection_count = 0
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = super().__new__(class_, *args, **kwargs)
        return class_._instance
    
    # Function to get a database connection.
    # This function connects to database with the name `database.db`
    def get_db_connection(self):
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        self.__db_connection_count += 1
        return connection
    
    def get_db_count(self):
        return self.__db_connection_count

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    return DBFactory().get_db_connection()

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

def get_post_count():
    connection = get_db_connection()
    post_count = connection.execute('SELECT SUM(1) AS COUNT_POSTS FROM posts').fetchone()
    connection.close()
    return post_count

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      app.logger.info('Article "'+post['title']+'" - retrived!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# healthcheack endpoint
@app.route("/healthz")
def healthz():
    result = { "result": " OK - healthy"}
    return jsonify(result);

@app.route("/metrics")
def metrics():
    
    # Question: New connection will be opened with each /metrics call, is this a problem?
    post_count_row = get_post_count()
    
    # Question: is it just show active connection?
    db_count = DBFactory().get_db_count()

    metrics_result = {
        "db_connection_count": db_count,
        "post_count": post_count_row['COUNT_POSTS'],
    }
    return jsonify(metrics_result)

from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(levelname)s:%(module)s:[%(asctime)s], %(message)s",
                "datefmt": "%Y-%m-%d, %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
)

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
