from . import api
from .authentication import auth
from ..models import Comment, Permission
from flask import jsonify, request, url_for, current_app

@api.route('/comments/')
@auth.login_required
def get_comments():
    page = request.args.get('page', 1, type=int)
    
    pagination = Comment.query.paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)

    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)

    return jsonify({ 'comments': [comment.to_json() for comment in comments],
                     'prev': prev,
                     'next': next,
                     'count': pagination.total })

@api.route('/comments/<int:id>/')
@auth.login_required
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())
