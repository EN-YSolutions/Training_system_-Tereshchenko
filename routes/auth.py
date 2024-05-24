from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from models import User, db

auth_bp = Blueprint('auth', __name__)

'''
# Регистрация
@auth_bp.route('/register/', methods=['GET', 'POST'])
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        user_id = session['user_id']
        return redirect(url_for('main.dashboard'))
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
                return redirect(url_for('auth.login'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')

    return render_template('auth.html', register=True)


# Авторизация
@auth_bp.route('/login/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user_id = session['user_id']
        return redirect(url_for('main.dashboard'))

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
                    session['is_admin'] = True
                
                else:
                    session.pop('is_admin', None)  # Удаляем is_admin из сессии, если пользователь не является администратором

                flash('Успешная авторизация')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Неправильный логин или пароль.')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')

    return render_template('auth.html', login=True)

# Выход из аккаунта
@auth_bp.route('/logout/')
@auth_bp.route('/logout')
def logout():
    # Создаем объект ответа
    res = make_response(redirect(url_for('main.index')))

    # Удаляем куки по имени
    res.set_cookie('session', '', expires=0)

    # Очищаем данные сессии
    session.clear()

    return res
'''
