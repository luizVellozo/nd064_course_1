import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

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

    def check_connection(self):
        connection = self.get_db_connection()
        if connection is None:
            return False
        post_table = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'").fetchone()
        connection.close()
        return post_table is not None and post_table['name'] == 'posts'
    
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
    try:
        if DBFactory().check_connection():
            result = { "result": " OK - healthy"}
            return jsonify(result)
        else:
            result = { "result": "ERRO - unhealthy"}
            return jsonify(result), 500
    except Exception as e:
        app.logger.error('database healthy check fail: '+str(e))
        result = { "result": "ERRO - unhealthy"}
        return jsonify(result), 500

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



# start the application on port 3111
if __name__ == "__main__":

    # config logs, set logger to handle STDOUT and STDERR 
    #stdout_handler = logging.StreamHandler(sys.stdout)
    #stderr_handler =  logging.StreamHandler(sys.stderr)
    handlers = [logging.StreamHandler()]
    format_output = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)

    app.run(host='0.0.0.0', port='3111', debug=True)
