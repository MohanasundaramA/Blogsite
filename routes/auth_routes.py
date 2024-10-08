from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import bcrypt
from db_utils import get_user_by_email, insert_user

auth_bp = Blueprint('auth_bp', __name__)

# Registration route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        form = request.form
        email, role, password = form['email'], form['role'], form['password']

        if get_user_by_email(email):
            flash("Email already exists")
            return redirect(url_for('auth_bp.register'))

        if role == "admin" and form['verification_code'] != "123456":
            flash("Incorrect verification code")
            return redirect(url_for('auth_bp.register'))

        insert_user(form['username'], email, form['mobile'], bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(), role)
        flash("Registration successful")
        return redirect(url_for('auth_bp.login_post'))
    
    return render_template('register.html')

# Login route
@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == "POST":
        user = get_user_by_email(request.form['email'])

        if user and bcrypt.checkpw(request.form['password'].encode(), user['password'].encode()):
            session.update({'email': user['email'], 'username': user['username']})
            return redirect(url_for('blog_bp.home'))

        flash("Invalid credentials")
    
    return render_template('login.html')

# Logout route
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for('auth_bp.login_post'))
