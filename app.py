from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from mysql.connector import Error
from config.db import db_connection
from datetime import datetime
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

# Custom filter for formatting datetime
@app.template_filter('format_datetime')
def format_datetime(value):
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%I:%M %p   %B %d, %Y')

# Database utility functions
def get_user_by_username(username):
    cursor = db_connection.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()
    return user

def insert_user(username, password):
    cursor = db_connection.cursor()
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, password))
    db_connection.commit()
    cursor.close()

def get_user_blogs(username):
    cursor = db_connection.cursor(dictionary=True)
    query = "SELECT * FROM blogs WHERE username = %s ORDER BY inserted_time DESC"
    cursor.execute(query, (username,))
    blogs = cursor.fetchall()
    cursor.close()
    return blogs

def get_all_blogs():
    cursor = db_connection.cursor(dictionary=True)
    query = "SELECT * FROM blogs ORDER BY inserted_time DESC"
    cursor.execute(query)
    blogs = cursor.fetchall()
    cursor.close()
    return blogs

def get_total_blogs():
    cursor = db_connection.cursor()
    query = "SELECT COUNT(*) AS total FROM blogs"
    cursor.execute(query)
    total = cursor.fetchone()
    cursor.close()
    return total

def get_user_blog_count(username):
    cursor = db_connection.cursor()
    query = "SELECT COUNT(*) AS total FROM blogs WHERE username = %s"
    cursor.execute(query, (username,))
    total = cursor.fetchone()
    cursor.close()
    return total

# Route for registering a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    
    username = request.form.get('username')
    password = request.form.get('password')

    if get_user_by_username(username):
        flash("Username already exists")
        return redirect(url_for('register'))

    try:
        insert_user(username, password)
        flash("Username registered Successfully")
        return redirect(url_for('login_post'))
    except Error as e:
        print(f"Error inserting user: {e}")
        return jsonify({"message": "Internal server error"}), 500

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == "GET":
        return render_template('login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')

    user = get_user_by_username(username)
    if user and user['password'] == password:
        session['username'] = username
        return redirect(url_for('home'))
    else:
        flash("Invalid credentials")
        return redirect(url_for('login_post'))

# Home route to display blogs
@app.route('/home', methods=['GET'])
def home():
    username = session.get("username")

    if username:
        show_mine_only = request.args.get('show_mine_only') == 'true'
        
        if show_mine_only:
            blogs = get_user_blogs(username)
            total_blogs = get_user_blog_count(username)
        else:
            blogs = get_all_blogs()
            total_blogs = get_total_blogs()

        return render_template('home.html', username=username, blogCount=total_blogs, blogs=blogs, show_mine_only=show_mine_only)
    else:
        flash("You must be logged in to access the page")
        return redirect(url_for('login_post'))
    
# Route to add a new blog
@app.route('/add-blog', methods=['POST'])
def add_blog():
    username = session.get('username')
    new_blog_content = request.form.get('new_blog_content')

    if not username:
        flash("You must be logged in to add a blog")
        return redirect(url_for('login_post'))

    try:
        cursor = db_connection.cursor()
        insert_query = "INSERT INTO blogs (username, blog, inserted_time) VALUES (%s, %s, NOW())"
        cursor.execute(insert_query, (username, new_blog_content))
        db_connection.commit()
        cursor.close()  
        return redirect(url_for('home'))

    except Error as e:
        print(f"Error inserting blog: {e}")
        return jsonify({"message": "Internal server error"}), 500

# Route to edit a blog
@app.route('/edit-blog/<int:blog_id>', methods=['GET'])
def edit_blog(blog_id):
    cursor = db_connection.cursor(dictionary=True)
    query = "SELECT * FROM blogs WHERE id = %s"
    cursor.execute(query, (blog_id,))
    blog = cursor.fetchone()
    cursor.close()

    blog['editing'] = True

    return render_template('home.html', username=session['username'], blogCount=0, blogs=[blog], editing=True)

# Route to update a blog
@app.route('/update-blog/<int:blog_id>', methods=['POST'])
def update_blog(blog_id):
    new_content = request.form.get('new_content')

    cursor = db_connection.cursor()
    update_query = "UPDATE blogs SET blog = %s WHERE id = %s"
    cursor.execute(update_query, (new_content, blog_id))
    db_connection.commit()
    cursor.close()

    return redirect(url_for('home'))

# Route to cancel blog editing
@app.route('/cancel-edit', methods=['GET'])
def cancel_edit():
    return redirect(url_for('home'))

# Route to delete a blog
@app.route('/delete-blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    cursor = db_connection.cursor()
    delete_query = "DELETE FROM blogs WHERE id = %s"
    cursor.execute(delete_query, (blog_id,))
    db_connection.commit()
    cursor.close()

    return redirect(url_for('home'))
  
# Route to log out the user 
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out Successfully")
    return redirect(url_for('login_post'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)
