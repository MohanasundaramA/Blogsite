from config.db import db_connection

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """Execute a query and return the result."""
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(query, params or ())
    result = cursor.fetchone() if fetchone else cursor.fetchall() if fetchall else None
    cursor.close()
    return result

def execute_commit(query, params=None):
    """Execute a query that modifies the database (INSERT, UPDATE, DELETE)."""
    cursor = db_connection.cursor()
    cursor.execute(query, params or ())
    db_connection.commit()
    cursor.close()

# User-related functions
def get_user_by_email(email):
    return execute_query("SELECT * FROM accounts WHERE email = %s", (email,), fetchone=True)

def insert_user(username, email, mobile, password, role):
    query = """
    INSERT INTO accounts (username, email, mobile, password, role, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
    """
    execute_commit(query, (username, email, mobile, password, role))

# Blog-related functions
def get_blog_by_id(blog_id):
    return execute_query("SELECT * FROM blogs WHERE id = %s", (blog_id,), fetchone=True)

def get_blog_comments(blog_id):
    query = '''
    SELECT r.reaction_id, r.comment_text, a.username, r.commented_date 
    FROM reactions r
    JOIN accounts a ON r.email = a.email
    WHERE blog_id = %s AND r.comment_text IS NOT NULL
    ORDER BY r.commented_date DESC
    '''
    return execute_query(query, (blog_id,), fetchall=True)

def get_likes_count(blog_id):
    return execute_query("SELECT COUNT(*) AS total FROM reactions WHERE blog_id = %s AND liked_time IS NOT NULL", (blog_id,), fetchone=True)['total']

def get_comments_count(blog_id):
    return execute_query("SELECT COUNT(*) AS total FROM reactions WHERE blog_id = %s AND comment_text IS NOT NULL", (blog_id,), fetchone=True)['total']

def get_reaction_by_id(reaction_id):
    query = "SELECT liked_time, comment_text FROM reactions WHERE reaction_id = %s"
    return execute_query(query, (reaction_id,), fetchone=True)

def get_existing_comment(email, blog_id):
    query = "SELECT reaction_id FROM reactions WHERE email = %s AND blog_id = %s AND commented_date IS NULL"
    reaction = execute_query(query, (email, blog_id), fetchone=True)
    return reaction['reaction_id'] if reaction else None

def get_all_user_reactions(email, blog_id):
    query = """
    SELECT reaction_id, liked_time, commented_date 
    FROM reactions 
    WHERE email = %s AND blog_id = %s
    """
    return execute_query(query, (email, blog_id), fetchall=True)

def get_user_like_status(email, blog_id):
    query = "SELECT reaction_id, commented_date FROM reactions WHERE email = %s AND blog_id = %s AND liked_time IS NOT NULL"
    reaction = execute_query(query, (email, blog_id), fetchone=True)
    return reaction if reaction else None

# Blog fetching and modification functions
def get_blogs(query, params=None, email=None):
    blogs = execute_query(query, params, fetchall=True)
    for blog in blogs:
        blog['comments'] = get_blog_comments(blog['id'])
        blog['likes_count'] = get_likes_count(blog['id'])
        blog['comments_count'] = get_comments_count(blog['id'])
        like_status = get_user_like_status(email, blog['id']) if email else None
        blog['liked_time'] = like_status['reaction_id'] if like_status else None
    return blogs

def get_blogs_by_author(email):
    query = """
    SELECT b.*, a.* 
    FROM blogs b
    JOIN accounts a ON b.email = a.email 
    WHERE a.email = %s
    ORDER BY b.inserted_time DESC
    """
    return get_blogs(query, (email,), email)

def get_all_blogs(email):
    query = """
    SELECT b.*, a.* 
    FROM blogs b
    JOIN accounts a ON b.email = a.email 
    ORDER BY b.inserted_time DESC
    """
    return get_blogs(query, email=email)

def insert_blog(email, content):
    query = "INSERT INTO blogs (email, blog, inserted_time) VALUES (%s, %s, NOW())"
    execute_commit(query, (email, content))

def update_blog_content(blog_id, new_content):
    execute_commit("UPDATE blogs SET blog = %s, inserted_time = NOW() WHERE id = %s", (new_content, blog_id,))

def delete_blog_by_id(blog_id):
    execute_commit("DELETE FROM blogs WHERE id = %s", (blog_id,))

# Comment-related functions
def insert_comment(email, blog_id, comment_text):
    query = """
    INSERT INTO reactions (email, blog_id, comment_text, commented_date) 
    VALUES (%s, %s, %s, NOW())
    """
    execute_commit(query, (email, blog_id, comment_text))

def update_reaction_comment(reaction_id, new_comment, date):
    query = "UPDATE reactions SET comment_text = %s, commented_date = %s WHERE reaction_id = %s"
    execute_commit(query, (new_comment, date, reaction_id))

def delete_reaction(reaction_id):
    query = "DELETE FROM reactions WHERE reaction_id = %s"
    execute_commit(query, (reaction_id,))

# Like-related functions
def insert_like(email, blog_id):
    query = """
    INSERT INTO reactions (email, blog_id, liked_time, commented_date)
    VALUES (%s, %s, NOW(), NULL)
    """
    execute_commit(query, (email, blog_id))

def update_like_status(reaction_id, liked_time):
    execute_commit("UPDATE reactions SET liked_time = %s WHERE reaction_id = %s", (liked_time, reaction_id))

# Blog statistics functions
def get_total_blogs():
    return execute_query("SELECT COUNT(*) AS total FROM blogs", fetchone=True)['total']

def get_blog_count_by_author(email):
    return execute_query("SELECT COUNT(*) AS total FROM blogs WHERE email = %s", (email,), fetchone=True)['total']
