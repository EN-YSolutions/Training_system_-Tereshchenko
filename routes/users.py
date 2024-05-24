from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response, abort
from models import User, Course, Course_Feedback, db

users_bp = Blueprint('user', __name__)

'''
@users_bp.route('/user/')
@users_bp.route('/user')
def index():
    return redirect(url_for('main.dashboard'))


@users_bp.route('/user/<username>/')
@users_bp.route('/user/<username>')
def view_user(username):
    user = User.query.filter_by(username=username).first()

    if user:
        # Подгружаем отзывы других пользователей на профиль преподавателя
        if user.role == 'teacher':
            
            feedbacks = db.session.query(
                Course_Feedback.text,
                Course_Feedback.date,
                Course.title,
                User.username,
                User.name,
                Course.url
            ).join(
                Course, Course.id == Course_Feedback.course_id
            ).join(
                User, User.id == Course_Feedback.author_id
            ).filter(
                Course.author_id == user.id
            ).order_by(
                Course_Feedback.date.desc()
            ).all()

            return render_template('user.html', user=user, course_feedbacks=feedbacks)
        else:
            return render_template('user.html', user=user)
    
    else:
        abort(404)
'''


