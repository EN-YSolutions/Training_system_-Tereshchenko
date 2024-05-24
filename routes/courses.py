from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User, Course, Course_Feedback, Group, Group_Members, db
from sqlalchemy import func

courses_bp = Blueprint('courses', __name__)
'''
@courses_bp.route('/course/<course_title>/', methods=['GET'])
@courses_bp.route('/course/<course_title>', methods=['GET'])
def view_course(course_title):
    course_title_lower = course_title.lower()
    course = Course.query.filter(func.lower(Course.title) == course_title_lower.replace('_', ' ')).first()

    if not course:
        return render_template('error.html', message='Course not found')

    # Проверяем, присоединен ли пользователь к группе курса
    is_user_joined = False
    if 'user_id' in session:
        user_id = session['user_id']
        group = Group.query.filter_by(course_id=course.id).first()
        if group:
            is_user_joined = Group_Members.query.filter_by(student_id=user_id, group_id=group.id).first() is not None

    return render_template('course.html', course=course, is_user_joined=is_user_joined)

@courses_bp.route('/courses/<course_title>/subscribe', methods=['POST'])
def subscribe(course_title):
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

        if user:
            course = Course.query.filter_by(title=course_title).first()

            if float(course.price.replace(" ?","").replace(",", ".")) > 0:
                print("")
            else:
                group = Group.query.filter_by(course_id = course.id).first()

                # Если группа бесплатного курса не существует, создаём новую
                if not group:
                    group = Group(course_id = course.id, title="Бесплатный курс " + course.title)
                    db.session.add(group)
                    db.session.commit()
                
            
                # Проверяем, есть ли пользователь уже в этой группе
                existing_member = Group_Members.query.filter_by(student_id=user.id, group_id=group.id).first()
                if not existing_member:
                    # Создаем новую запись в таблице Group_Members
                    new_member = Group_Members(student_id=user.id, group_id = group.id)
                    db.session.add(new_member)
                    db.session.commit()
        else:
            # Возвращаем ошибку или перенаправляем на страницу входа
            return redirect(url_for('auth.login')) 
        
        # Если пользователь успешно добавлен в группу, можно сделать редирект на страницу курса
        return redirect(url_for('courses.view_course', course_title=course_title))



@courses_bp.route('/courses/<course_title>/add_feedback', methods=['POST'])
def add_feedback(course_title):
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

        if user:
            course_title_lower = course_title.lower()
            course = Course.query.filter(func.lower(Course.title) == course_title_lower.replace('_', ' ')).first()

            if course:
                feedback_text = request.form['feedback_text']
                new_feedback = Course_Feedback(course_id=course.id, author_id=user.id, text=feedback_text)
                db.session.add(new_feedback)
                db.session.commit()
            else:
                flash('Course not found.')
        else:
            flash('User not found.')

        return redirect(url_for('courses.view_course', course_title=course_title))
    else:
        return redirect(url_for('auth.login'))

@courses_bp.route('/course/<course_title>/lesson/<lesson>/')
@courses_bp.route('/course/<course_title>/lesson/<lesson>')
def view_lesson(course_title, lesson):
    course_title_lower = course_title.lower()
    course = Course.query.filter(func.lower(Course.title) == course_title_lower.replace('_', ' ')).first()
'''
