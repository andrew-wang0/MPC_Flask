from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user, login_user, LoginManager

from mysite.forms import LoginForm, SignUpForm
from mysite.models import db, User

auth = Blueprint('auth', __name__)

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to access this page', 'danger')
    return redirect(url_for('auth.login', next=request.path))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('views.index'))
        else:
            flash('Login Unsuccessful. Invalid email and password combination.', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('auth/logout.html')


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User(email=email, password=password)

        if User.query.filter(User.email == email).first():
            flash(f'{email} has already been registered. Try logging in instead.', 'danger')
        else:
            db.session.add(user)
            db.session.commit()

            flash(f'User Registered: {user.email}', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/sign_up.html', form=form)
