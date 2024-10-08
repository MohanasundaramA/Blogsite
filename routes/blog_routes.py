from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, session
import os
from datetime import datetime
from db_utils import *
from utils import handle_file_upload

blog_bp = Blueprint('blog_bp', __name__)

# Home route to display blogs
@blog_bp.route('/home')
def home():
    email = session.get("email")
    if not email:
        flash("You must be logged in to access the page")
        return redirect(url_for('auth_bp.login_post'))

    show_mine_only = request.args.get('show_mine_only') == 'true'
    blogs = get_blogs_by_author(email) if show_mine_only else get_all_blogs(email)
    total_blogs = get_blog_count_by_author(email) if show_mine_only else get_total_blogs()
    user_role = get_user_by_email(email)['role']

    return render_template('home.html', email=email, username=session['username'], 
                           blogCount=total_blogs, blogs=blogs, show_mine_only=show_mine_only, user_role=user_role)

# Route to add a blog
@blog_bp.route('/add-blog', methods=['POST'])
def add_blog():
    email = session.get("email")
    if not email:
        flash("You must be logged in to add a blog")
        return redirect(url_for('blog_bp.home'))

    blog_content = request.form.get('new_blog_content')
    file = request.files.get('blog_image')
    filename = handle_file_upload(file) if file else None

    insert_blog(email, blog_content, filename)
    return redirect(url_for('blog_bp.home'))

# Route to edit a blog
@blog_bp.route('/edit-blog/<int:blog_id>')
def edit_blog(blog_id):
    blog = get_blog_by_id(blog_id)
    return render_template('home.html', email=session['email'], username=session['username'], blogs=[blog], editing=True)

# Route to update a blog
@blog_bp.route('/update-blog/<int:blog_id>', methods=['POST'])
def update_blog(blog_id):
    new_content = request.form.get('new_content')
    image_deleted = request.form.get('image_deleted') == 'true'

    blog = get_blog_by_id(blog_id)
    existing_image = blog["image_url"]

    if image_deleted and existing_image:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], existing_image)
        if os.path.exists(image_path):
            os.remove(image_path)
        existing_image = ""

    file = request.files.get('blog_image')
    new_image = handle_file_upload(file) if file else existing_image

    update_blog_content(blog_id, new_content, new_image)
    return redirect(url_for('blog_bp.home'))

# Route to delete a blog
@blog_bp.route('/delete-blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    blog = get_blog_by_id(blog_id)
    existing_image = blog["image_url"]

    if existing_image:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], existing_image)
        if os.path.exists(image_path):
            os.remove(image_path)

    delete_blog_by_id(blog_id)
    return redirect(url_for('blog_bp.home'))

# Route to cancel blog edit
@blog_bp.route('/cancel-edit', methods=['GET'])
def cancel_edit():
    return redirect(url_for('blog_bp.home'))

# Route to add a comment
@blog_bp.route('/add-comment/<int:blog_id>', methods=['POST'])
def add_comment(blog_id):
    email = session.get('email')
    if not email:
        flash("You must be logged in to comment")
        return redirect(url_for('blog_bp.home'))

    new_content = request.form['comment_content']
    reaction = get_existing_comment(email, blog_id)

    if reaction:
        update_reaction_comment(reaction, new_content, datetime.now())
    else:
        insert_comment(email, blog_id, new_content)

    return redirect(url_for('blog_bp.home'))

# Route to edit a comment
@blog_bp.route('/edit-comment/<int:reaction_id>', methods=['POST'])
def edit_comment(reaction_id):
    email = session.get('email')
    if not email:
        flash("You must be logged in to edit a comment")
        return redirect(url_for('blog_bp.home'))

    update_reaction_comment(reaction_id, request.form.get('new_comment'), datetime.now())
    return redirect(url_for('blog_bp.home'))

# Route to delete a comment
@blog_bp.route('/delete-comment/<int:reaction_id>', methods=['POST'])
def delete_comment(reaction_id):
    email = session.get('email')
    if not email:
        flash("You must be logged in to delete a comment")
        return redirect(url_for('blog_bp.home'))

    reaction = get_reaction_by_id(reaction_id)
    if reaction and reaction['liked_time'] is None:
        delete_reaction(reaction_id)
    else:
        update_reaction_comment(reaction_id, None, None)

    return redirect(url_for('blog_bp.home'))

# Route to like a blog
@blog_bp.route('/like-blog/<int:blog_id>', methods=['POST'])
def like_blog(blog_id):
    email = session.get('email')
    if not email:
        return redirect(url_for('blog_bp.home'))

    like = request.form.get('like') == 'true'
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

    return redirect(url_for('blog_bp.home'))
