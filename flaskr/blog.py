from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from bson import ObjectId
from datetime import datetime

bp = Blueprint('blog',__name__)

@bp.route("/")
def index():
    db = get_db()
    ##posts = db.execute(
    ##    'SELECT p.id, title, body, created, author_id, username'
    ##    ' FROM post p JOIN user u ON p.author_id = u.id'
    ##    ' ORDER BY created DESC'
    ##).fetchall()
    posts = list(db.posts.aggregate([{"$project":{"_id":0, "id":str("$_id"), "title":1, "body":1, "created":1, "author_id":str("$author_id"), "username":1}},{"$sort":{"created":-1}}]))
    
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            ##db.execute(
            ##    'INSERT INTO post(title, body, author_id)'
            ##    ' VALUES (?,?,?)',
            ##    (title, body, g.user['id'])
            ##)
            ##db.commit()
            db.posts.insert_one({"title":title, "body":body, "author_id":ObjectId(g.user['user_id']),"username":g.user['username'], "created":datetime.now()})
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    ##post = get_db().execute(
    ##    'SELECT p.id, title, body, created, author_id, username'
    ##    ' FROM post p JOIN user u ON p.author_id = u.id'
    ##    ' WHERE p.id = ?',
    ##    (id,)
    ##).fetchone()
    post = list(get_db().posts.aggregate([{"$match":{"_id":ObjectId(id)}},{"$project":{"id":str("$_id"),"title":1,"body":1,"created":1,"author_id":str("$author_id"),"username":1}}]))[0]

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['user_id']:
        abort(403)

    return post

@bp.route('/<id>/update', methods=('GET','POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            ##db.execute(
            ##    'UPDATE post SET title=?, body=?'
            ##    ' WHERE id = ?',
            ##    (title, body, id)
            ## )
            ##db.commit()
            db.posts.update_one({"_id":ObjectId(id)},{"$set":{"title":title,"body":body}})
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post=post)

@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.posts.delete_one({"_id":ObjectId(id)})
    return redirect(url_for('blog.index'))

    




