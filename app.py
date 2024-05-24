import os, random
from dotenv import load_dotenv
# from routes import register_routes
from models import db, User, Group, Group_Members, Course, Course_Feedback, Test, Request
from sqlalchemy import event, func, cast, Numeric
from flask import Flask, render_template, render_template_string, url_for, request, session, redirect, flash, abort, make_response, jsonify


app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.secret_key = os.environ['SECRET_KEY']
db.init_app(app)
# register_routes(app)

# --------------------------------------------- Главная страница --------------------------------------------------
@app.get('/')
def index():
    random_courses = Course.query.order_by(func.random()).limit(6).all()
    random_feedbacks = Course_Feedback.query.order_by(func.random()).limit(12).all()
    return render_template('index.html', random_courses=random_courses, random_feedbacks=random_feedbacks)

# --------------------------------------------- Пользователи --------------------------------------------------
@app.context_processor
def inject_user():
    if 'user_id' in session:
        # Получаем объект пользователя из базы данных по user_id из сессии
        account = User.query.get(session['user_id'])
        return dict(account=account)  # Возвращаем словарь с переменной user
    else:
        return dict(account=None)  # Возвращаем пустой объект user, если пользователь не авторизован
        
@app.get('/user/')
@app.get('/user')
def null_user():
    return redirect(url_for('dashboard'))


@app.get('/user/<username>/')
@app.get('/user/<username>')
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

# Функция для генерации случайного цвета
def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

# Назначение случайного цвета пользователям без аватарок
@event.listens_for(User, 'before_insert')
def assign_random_color(mapper, connection, target):
    if not target.url:
        target.color = generate_random_color()

def assign_random_colors_to_users():
    users = User.query.all()
    for user in users:
        if not user.url:
            user.color = generate_random_color()
    db.session.commit()        



# ------------------------------------------------ Каталог ----------------------------------------------------
        
@app.route('/catalog/', methods=['GET', 'POST'])
@app.route('/catalog', methods=['GET', 'POST'])
def catalog():
    if request.method == 'POST':
        min_price = request.form.get('min_price', type=int)
        max_price = request.form.get('max_price', type=int)
        filter_types = request.form.getlist('type')

        query = Course.query
        if min_price is not None:
            query = query.filter(cast(Course.price, Numeric) >= min_price)
        if max_price is not None:
            query = query.filter(cast(Course.price, Numeric) <= max_price)
        if filter_types:
            query = query.filter(Course.type.in_(filter_types))
        
        courses = query.all()
        return render_template_string('{% include "catalog_content.html" %}', courses=courses)
    
    return render_template('catalog.html', courses=Course.query.all())



# ------------------------------------------------- Курсы ------------------------------------------------------  
@app.route('/course/<course_title>/', methods=['GET'])
@app.route('/course/<course_title>', methods=['GET'])
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

@app.route('/courses/<course_title>/subscribe', methods=['POST'])
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
            return redirect(url_for('login')) 
        
        # Если пользователь успешно добавлен в группу, редирект на страницу курса
        return redirect(url_for('view_course', course_title=course_title))

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

@app.route('/course/<course_title>/lesson/<lesson>/')
@app.route('/course/<course_title>/lesson/<lesson>')
def view_lesson(course_title, lesson):
    course_title_lower = course_title.lower()
    course = Course.query.filter(func.lower(Course.title) == course_title_lower.replace('_', ' ')).first()



# ------------------------------------------------- Тесты ------------------------------------------------------
@app.get('/tests')
def tests():
    courses_with_tests = Course.query.filter(Course.tests.any()).all()
    return render_template('tests.html', courses_with_tests=courses_with_tests)

@app.get('/tests/<id>/')
@app.get('/tests/<id>')
def view_test(id):
    test = Test.query.filter_by(id=id).first_or_404()
    return render_template('test.html', test=test)



# ------------------------------------------------ Менеджер ----------------------------------------------------
@app.post('/submit_request')
def submit_request():
    # Проверяем наличие всех необходимых параметров в запросе
    if 'name' not in request.form or 'phone' not in request.form or 'email' not in request.form:
        return jsonify({'message': 'Все поля формы должны быть заполнены'}), 400

    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']


    # Проверяем, есть ли уже заявка с такой же почтой и фамилией
    existing_request = Request.query.filter_by(name=name, email=email, status='pending').first()
    if existing_request:
        return jsonify({'message': 'Ваша заявка уже на рассмотрении'}), 400
    

    # Создаем новую заявку
    new_request = Request(name=name, phone=phone, email=email)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'message': 'Ваша заявка была успешно отправлена!'}), 200

def check_manager():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

        if user and user.role == "manager":
            return True
    return False

@app.route('/manager', methods=['GET', 'POST'])
def manager():
    if request.method == 'POST':
        status = request.form.get('status')

        query = Request.query
        if status != 'all':  # Учтите значение 'all'
            query = query.filter_by(status=status)
        
        requests = query.order_by(Request.date.desc()).all()
        return render_template('manager_requests.html', requests=requests)
    
    return render_template('manager.html', requests=Request.query.order_by(Request.date.desc()).all())

@app.post('/manager/processed_request/<request_id>')
def manager_accept_request(request_id):
    if not check_manager():
        return jsonify({'error': 'Доступ запрещен. Необходима роль менеджера.'}), 403
    
    request_record = Request.query.get_or_404(request_id)
    request_record.status = 'processed'
    db.session.commit()
    return jsonify({'message': 'Заявка была обработана'})

@app.post('/manager/processing_request/<request_id>')
def manager_processing_request(request_id):
    if not check_manager():
        return jsonify({'error': 'Доступ запрещен. Необходима роль менеджера.'}), 403
    
    request_record = Request.query.get_or_404(request_id)
    request_record.status = 'processing'
    db.session.commit()
    return jsonify({'message': 'Заявка в обработке'})


# --------------------------------------------- Аутентификация -------------------------------------------------
@app.route('/register/', methods=['GET', 'POST'])
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

    return render_template('auth.html', register=True)


# Авторизация
@app.route('/login/', methods=['GET', 'POST'])
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
                
                session['user_username'] = user.username

                if user.role == 'admin':
                    session['role'] = 'admin'
                elif user.role == 'manager':
                    session['role'] = 'manager'
                elif user.role == 'teacher':
                    session['role'] = 'teacher'
                else:
                    session['role'] = 'student' 

                flash('Успешная авторизация')
                return redirect(url_for('dashboard'))
            else:
                flash('Неправильный логин или пароль.')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')

    return render_template('auth.html', login=True)

# Выход из аккаунта
@app.route('/logout/')
@app.route('/logout')
def logout():
    # Создаем объект ответа
    res = make_response(redirect(url_for('index')))

    # Удаляем куки по имени
    res.set_cookie('session', '', expires=0)

    # Очищаем данные сессии
    session.clear()

    return res    


# --------------------------------------------- ДРУГИЕ МОДУЛИ -------------------------------------------------
@app.get('/dashboard/')
@app.get('/dashboard')
def dashboard():
    # Проверяем, есть ли id пользователя в сеансе
    if 'user_id' in session:
        username = session['user_username']
        return render_template('dashboard.html', username=username)
    else:
        flash('You need to log in first.')
        return redirect(url_for('login'))


@app.get('/chat')
def chat():
    return render_template('module.html', chat=True)

@app.get('/admin')
def admin():
    return render_template('module.html', admin=True)

# Обработка ошибок
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        assign_random_colors_to_users()

    app.run(debug=True)
    