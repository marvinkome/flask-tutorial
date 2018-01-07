from . import api
from .authentication import auth
from flask_login import login_required
from ..models import Post, Permission, Comment
from flask import jsonify, request, url_for, current_app, g
from .decorators import permission_required
from .errors import forbidden
from .. import db

@api.route('/posts/')
@auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKY_POST_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)

    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)

    return jsonify({ 'posts': [post.to_json() for post in posts],
                     'prev': prev,
                     'next': next,
                     'count': pagination.total })

@api.route('/post/<int:id>/')
@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_json()), 201,\
        {'location': url_for('api.get_post', id=post.id, _external=True)}

@api.route('/posts/<int:id>/', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Access Denied')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())

@api.route('/posts/<int:id>/comments/')
@auth.login_required
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False
    )
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', page=page-1, _external=True)

    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comments', page=page+1, _external=True)

    return jsonify({ 'comments': [comment.to_json() for comment in comments],
                     'prev': prev,
                     'next': next,
                     'count': pagination.total })


@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post

    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_json()), 201,\
        {'location': url_for('api.get_post_comments', id=post.id, _external=True)}
