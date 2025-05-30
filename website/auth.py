from flask import current_app as app, render_template, redirect, url_for, flash, request
from .models import db, User
from flask_login import login_user, logout_user, login_required, current_user


# registration route
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'general')  # Default to 'general' if role is not provided
        if User.query.filter_by(email = email).first():
            flash('Email already registered.')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('register'))
        user = User(username = username, email = email, role = role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User registered successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            if user.is_admin():
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template("login.html")

#logout route
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))
