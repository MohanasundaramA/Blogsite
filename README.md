
# Blog Site

## Overview
Welcome to the Blog Site! This platform allows users to share their thoughts and ideas through blog posts. It features role-based access, where admins and users have distinct permissions.

Admin: Can create, edit, delete blogs, and manage images in posts, as well as like and comment on blogs.</br>
User: Can only view all blogs, like posts, and leave comments but cannot create, edit, or delete blogs.

The front-end is built using HTML, CSS, and JavaScript to provide a responsive and intuitive interface. The back-end is powered by Flask, a lightweight Python web framework. The platform integrates a MySQL database for managing user, blog, and interaction data.


## Features
**Admin Role:**
- Create, Edit, and Delete Blogs: Admins can manage blog content.
- Add, Edit, and Delete Images: Admins can manage images associated with blog posts.
- Like and Comment on Blogs: Admins can interact with blogs by liking and commenting.
- View All Blogs: Admins can browse posts from all users.</br>

**User Role:**
- View All Blogs: Users can browse all blog posts.
- Like and Comment on Blogs: Users can interact with blogs by liking and leaving comments. 

## Tech Stack
- Front-End: HTML, CSS, JavaScript
- Back-End: Flask (Python)
- Database: MySQL

## Prerequisites
- Python 3.x
- Flask
- MySQL
- MySQL Connector for Python

## Project Structure
blog-site/\
│\
├── templates/\
│   ├── home.html\
│   ├── login.html\
│   └── register.html\
│\
├── static/\
│   ├── images/\
│   ├── uploads/\
│   ├── home.css\
│   ├── login.css\
│   ├── register.css\
│\
├── routes/\
│   ├── auth_routes.py\
│   ├── blog_routes.py\
│\
├── config/\
│   └── db.py\
│\
├── db_utils.py\
├── utils.py\
└── app.py

## Setup Instructions
1. Clone the Repository
```
git clone "REPO_LINK"
cd 
```
2. Install Dependencies
```
pip install flask mysql-connector-python
```

3. Database Configuration
```
db_connection = mysql.connector.connect(
    host="your_host",
    user="your_username",
    password="your_password",
    database="your_database"
)
```

4. Database Schema
```
-- Table for user accounts
CREATE TABLE accounts (
    username VARCHAR(255) NOT NULL,      
    email VARCHAR(255) PRIMARY KEY,   
    mobile VARCHAR(10) NOT NULL,  
    role VARCHAR(10) NOT NULL,
    password VARCHAR(255) NOT NULL, 
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table for blogs
CREATE TABLE blogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    blog TEXT NOT NULL,
    image_url TEXT,
    inserted_time DATETIME NOT NULL,
    FOREIGN KEY (email) REFERENCES accounts(email)
);

-- Table for likes and comments
CREATE TABLE reactions (
    reaction_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    blog_id INT NOT NULL,
    comment_text TEXT,      
    commented_date DATETIME DEFAULT CURRENT_TIMESTAMP,  
    liked_time DATETIME,                   
    FOREIGN KEY (email) REFERENCES accounts(email) ON DELETE CASCADE,
    FOREIGN KEY (blog_id) REFERENCES blogs(id) ON DELETE CASCADE
);

```
5. Run the Application
```
python app.py
```


https://github.com/user-attachments/assets/a9d1f2e2-9b96-4456-b482-4c7031e8b495


## Conclusion
This blog site provides a platform for users to share and engage with blog content. It supports role-based access control where admins have full control over blog content, including the ability to manage images, while users can view, like, and comment. The system ensures a seamless user experience with a well-structured front-end and a robust back-end powered by Flask and MySQL.
