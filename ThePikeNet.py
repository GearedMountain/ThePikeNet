pikenetVersion = 1.0
from flask import Flask, request, send_from_directory, render_template, session, Response, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import text
from dotenv import load_dotenv
from logic.Routing import basic_routing  # import the Blueprint
from logic.AdminRouting import admin_routing  # import the Blueprint
import os 
import random

load_dotenv()

app = Flask(__name__)
app.register_blueprint(basic_routing, url_prefix='/')
app.register_blueprint(admin_routing, url_prefix='/admin')

# Grab environment variables
secret_key = os.getenv("SECRET_KEY")
database_url = os.getenv("DATABASE_URL")

# Error if there is no databaseurl
if not database_url:
    raise ValueError("DATABASE_URL is not set or is empty")
    
# remove DATABASE_URL= from the variable because sqlalchemy is stupid
if database_url.startswith("DATABASE_URL="):
    database_url = database_url[len("DATABASE_URL="):]
  
app.config['SQLALCHEMY_DATABASE_URI'] = database_url


# REMOVE THIS ----------------------------------------------------------------------------
db = SQLAlchemy(app)
@app.route('/test_db')
def test_db_connection():
    try:
        # Try to execute a basic query to test the connection
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")) 
        rows = result.fetchall()
        rows_dict = [{"table_name": row[0]} for row in rows]
        print(rows[0])
        return jsonify(rows_dict), 200

    except Exception as e:
        return f"Error connecting to the database: {str(e)}", 500
# REMOVE THIS ----------------------------------------------------------------------------

# Track current users with a session
SET_ACTIVESESSIONS = set()

# @@@@@@@@@@@@@@@@@@@@@@@@ SERVING IMAGES @@@@@@@@@@@@@@@@@@@@@@@
# Serve images from the 'images/official' folder
@app.route('/images/official/<filename>')
def get_official_image(filename):
    # Define the path to the 'images/official' folder
    image_folder = os.path.join(app.root_path, 'images', 'official')
    return send_from_directory(image_folder, filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
if __name__ == '__main__':
	app.run(debug=True