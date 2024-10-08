from datetime import datetime
from flask import Flask
from routes.auth_routes import auth_bp
from routes.blog_routes import blog_bp
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Custom filter to format time since a post was made
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

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(blog_bp)

# Run the app
if __name__ == '__main__':
    app.run(port=3000, debug=True)
