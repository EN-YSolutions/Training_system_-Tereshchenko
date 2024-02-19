from flask import Flask, render_template, request, Response, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/educational-portal'
app.config['SECRET_KEY'] = 'qwerty'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'  # Указываем имя существующей таблицы
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    name = db.Column(db.Text, nullable=False)

    feedbacks = db.relationship('Course_Feedback', backref='user', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.String(50), nullable=False)  
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    
    feedbacks = db.relationship('Course_Feedback', backref='course', lazy=True)

class Course_Feedback(db.Model):
    __tablename__ = 'courses_feedbacks'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses', methods=['GET', 'POST'])
def courses():
    filter_type = request.args.get('type', 'all')

    if request.method == 'POST':
        filter_type = request.form.get('type', 'all')

    if filter_type == 'all':
        courses = Course.query.all()
    elif filter_type == 'short':
        courses = Course.query.filter_by(type='short').all()
    elif filter_type == 'long':
        courses = Course.query.filter_by(type='long').all()
    elif filter_type == 'intensive':
        courses = Course.query.filter_by(type='intensive').all()
    else:
        # Обработка некорректного значения параметра 'type'
        return render_template('error.html', message='Invalid filter type')

    return render_template('courses.html', courses=courses)

@app.route('/courses/<course_title>')
def view_course(course_title):
    course_title_lower = course_title.lower()
    course = Course.query.filter(func.lower(Course.title) == course_title_lower.replace('_', ' ')).first()

    if course:
    # Загрузим отзывы для этого курса
        feedbacks = Course_Feedback.query.filter_by(course_id=course.id).all()
        return render_template('course.html', course=course)
    else:
        return render_template('error.html', message='Course not found')
    
@app.route('/courses/<course_title>/add_feedback', methods=['POST'])
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

        return redirect(url_for('view_course', course_title=course_title))
    else:
        return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        user_id = session['user_id']
        return redirect(url_for('dashboard'))
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = "student"
            name = request.form['name']

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Пользователь с данным логином уже существует. Пожалуйста, введите другой.')
            else:
                new_user = User(username=username, password=password, role=role, name=name)
                db.session.add(new_user)
                db.session.commit()

                #flash('Registration successful! Please log in.')
                return redirect(url_for('login'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user_id = session['user_id']
        return redirect(url_for('dashboard'))

    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username, password=password).first()

            if user:
                # Аутентификация прошла успешно, устанавливаем id пользователя в сеансе
                session['user_id'] = user.id
                flash('Login successful!')
                return redirect(url_for('dashboard'))
            else:
                flash('Неправильный логин или пароль.')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Проверяем, есть ли id пользователя в сеансе
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

        if user:
            username = user.username
            return render_template('dashboard.html', username=username)
        else:
            flash('User not found.')
    else:
        flash('You need to log in first.')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Создаем объект ответа
    res = make_response(redirect(url_for('index')))

    # Удаляем куку по имени
    res.set_cookie('session', '', expires=0)

    # Очищаем данные сессии (по желанию)
    session.clear()

    return res

if __name__ == '__main__':
    app.run(debug=True)