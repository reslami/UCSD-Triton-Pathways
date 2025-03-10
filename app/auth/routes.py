from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, AccountUpdateForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or next_page.startswith('http://') or next_page.startswith('https://'):
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountUpdateForm(
        original_username=current_user.username,
        original_email=current_user.email
    )
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    elif form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.username = form.username.data
            current_user.email = form.email.data
            if form.new_password.data:
                current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('auth.account'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('auth/account.html', title='Account Settings', form=form)

@bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    form = AccountUpdateForm(
        original_username=current_user.username,
        original_email=current_user.email
    )
    
    if form.validate_on_submit():
        # Anonymize the user's incidents
        for incident in current_user.incidents:
            incident.reporter_id = None
        
        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        
        flash('Your account has been deleted. We\'re sorry to see you go!', 'info')
        return redirect(url_for('main.index'))
    
    flash('Invalid request. Please try again.', 'danger')
    return redirect(url_for('auth.account')) 