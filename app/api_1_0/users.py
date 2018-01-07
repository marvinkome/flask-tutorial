from . import api
from .authentication import auth
from flask_login import login_required
from ..models import User, Permission, Post
from flask import jsonify, request, url_for, current_app
from .decorators import permission_required
from .errors import forbidden
from .. import db

@api.route('/users/<int:id>/')
@auth.login_required
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/posts/')
@auth.login_required
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
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

@api.route('/users/<int:id>/timeline/')
@auth.login_required
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
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
