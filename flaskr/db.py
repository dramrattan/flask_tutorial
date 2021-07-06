import dotenv
from pymongo import MongoClient
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
from dotenv import load_dotenv
import dns
import os

load_dotenv()
MONGO_URL = os.environ['MONGO_URL']

def get_db():
    if 'db' not in g:
        mc = MongoClient(host=MONGO_URL)
        g.db = mc.get_database("flaskr")


    return g.db



def init_db():
    db = get_db()
    sqlL = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    sqlL.row_factory = sqlite3.Row

    users = sqlL.execute("SELECT  username, password FROM user").fetchall()
    for u in users:
        db.users.insert_one(dict(u))


    posts = sqlL.execute("SELECT title, body, created, username FROM post AS p INNER JOIN user AS u ON p.author_id = u.id").fetchall()
    for p in posts:
        d = dict(p)
        uid = db.users.find_one({"username":d['username']},{"_id":1})
        d['author_id'] = uid['_id']
        db.posts.insert_one(d)

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.cli.add_command(init_db_command)


