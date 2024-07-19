
# Project Title

## Overview
Welcome to the Blog Site! This platform provides users with a seamless experience to share their thoughts and ideas through blog posts. Users can easily register and log in to the application, allowing them to create, edit, and delete their own blog posts. Additionally, users can browse blogs posted by other members of the community.

The front-end of the application is crafted with HTML, CSS, and JavaScript, ensuring a responsive and user-friendly interface. The back-end is powered by Flask, a lightweight and powerful Python web framework. To efficiently manage user information and blog content, a MySQL database is integrated, ensuring data integrity and quick access.

## Features
- User registration and login
- View all blogs or only user-specific blogs
- Add new blogs
- Edit and delete existing blogs

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
│   ├── css/\
│   │   └── home.css\
│   │   └── login.css\
│   │   └── register.css\
│   └── images/\
│       └── logo.png\
│\
├── config/\
│   └── db.py\
│\
└── app.py

## Setup Instructions
1. Clone the Repository
```
git clone https://github.com/your-repo/blog-site.git
cd blog-site
```
2. Install Dependencies\
Ensure you have Python and pip installed. Then, install the required Python packages:

```
pip install flask mysql-connector-python
```

3. Database Configuration\
Create a MySQL database and configure the connection details in config/db.py:
```
import mysql.connector

db_connection = mysql.connector.connect(
    host="your_host",
    user="your_username",
    password="your_password",
    database="your_database"
)
```

4. Database Schema\
Execute the following SQL commands to create the necessary tables:
```
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE blogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    blog TEXT NOT NULL,
    inserted_time DATETIME NOT NULL,
    FOREIGN KEY (username) REFERENCES users(username)
);
```
5. Run the Application\
Start the Flask application:
```
python app.py
```
