import bcrypt
from flask import Flask, request, render_template, redirect, url_for, flash, session
from datetime import datetime
import secrets
from db_utils import (
    get_all_user_reactions, get_blog_count_by_author, get_blogs_by_author, get_existing_comment, get_reaction_by_id, 
    get_user_by_email, get_blog_by_id, get_user_like_status, insert_blog, insert_user, get_all_blogs, get_total_blogs, insert_comment, 
    update_blog_content, delete_blog_by_id, update_like_status, insert_like, update_reaction_comment, delete_reaction
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Time-since filter for blog post timestamps
@app.template_filter('time_since')
def time_since(inserted_time):
    diff = datetime.now() - inserted_time
    seconds = diff.total_seconds()
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}h"
    elif seconds < 2592000:
        return f"{int(seconds // 86400)}d"
    return f"{int(seconds // 2592000)} mon"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        form = request.form
        if form['role'] == "admin" and form['verification_code'] != "123456":
            flash("Incorrect verification code")
            return redirect(url_for('register'))
        if get_user_by_email(form['email']):
            flash("Email already exists")
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.hashpw(form['password'].encode('utf-8'), bcrypt.gensalt())
        insert_user(form['username'], form['email'], form['mobile'], hashed_password.decode('utf-8'), form['role'])

        flash("Registration successful")
        return redirect(url_for('login_post'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == "POST":
        user = get_user_by_email(request.form['email'])
        if user and bcrypt.checkpw(request.form['password'].encode('utf-8'), user['password'].encode('utf-8')):
            session['email'] = user['email']
            session['username'] = user['username']
            return redirect(url_for('home'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/home')
def home():
    email = session.get("email")
    if email:
        show_mine_only = request.args.get('show_mine_only') == 'true'
        blogs = get_blogs_by_author(email) if show_mine_only else get_all_blogs(email)
        total_blogs = get_blog_count_by_author(email) if show_mine_only else get_total_blogs()
        user_role = get_user_by_email(email)['role']
        return render_template('home.html', email=email, username=session['username'], 
                               blogCount=total_blogs, blogs=blogs, show_mine_only=show_mine_only, user_role=user_role)
    flash("You must be logged in to access the page")
    return redirect(url_for('login_post'))

@app.route('/add-blog', methods=['POST'])
def add_blog():
    email = session.get("email")
    if email:
        insert_blog(email, request.form.get('new_blog_content'))
    else:
        flash("You must be logged in to add a blog")
    return redirect(url_for('home'))

@app.route('/edit-blog/<int:blog_id>')
def edit_blog(blog_id):
    blog = get_blog_by_id(blog_id)
    return render_template('home.html', email=session['email'], username=session['username'], blogs=[blog], editing=True)

@app.route('/update-blog/<int:blog_id>', methods=['POST'])
def update_blog(blog_id):
    update_blog_content(blog_id, request.form.get('new_content'))
    return redirect(url_for('home'))

@app.route('/delete-blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    delete_blog_by_id(blog_id)
    return redirect(url_for('home'))

@app.route('/cancel-edit', methods=['GET'])
def cancel_edit():
    return redirect(url_for('home'))

@app.route('/add-comment/<int:blog_id>', methods=['POST'])
def add_comment(blog_id):
    email = session.get('email')
    if email:
        new_content = request.form['comment_content']
        reaction = get_existing_comment(email, blog_id)
        update_reaction_comment(reaction, new_content, datetime.now()) if reaction else insert_comment(email, blog_id, new_content)
    else:
        flash("You must be logged in to comment")
    return redirect(url_for('home'))

@app.route('/edit-comment/<int:reaction_id>', methods=['POST'])
def edit_comment(reaction_id):
    if session.get('email'):
        update_reaction_comment(reaction_id, request.form.get('new_comment'), datetime.now())
    else:
        flash("You must be logged in to edit a comment")
    return redirect(url_for('home'))

@app.route('/delete-comment/<int:reaction_id>', methods=['POST'])
def delete_comment(reaction_id):
    if session.get('email'):
        reaction = get_reaction_by_id(reaction_id)
        if reaction:
            if reaction['liked_time'] is None:
                delete_reaction(reaction_id)
            else:
                update_reaction_comment(reaction_id, None, None)
    else:
        flash("You must be logged in to delete a comment")
    return redirect(url_for('home'))

@app.route('/like-blog/<int:blog_id>', methods=['POST'])
def like_blog(blog_id):
    email = session.get('email')
    like = request.form.get('like') == 'true'
    if email:
        reactions = get_all_user_reactions(email, blog_id)
        if like and not any(reaction['liked_time'] for reaction in reactions):
            if reactions:
                update_like_status(reactions[0]['reaction_id'], datetime.now())
            else:
                insert_like(email, blog_id)
        elif not like:
            reaction = get_user_like_status(email, blog_id)
            if not reaction['commented_date']:
                delete_reaction(reaction['reaction_id'])
            update_like_status(reaction['reaction_id'], None)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("Logged out successfully")
    return redirect(url_for('login_post'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)