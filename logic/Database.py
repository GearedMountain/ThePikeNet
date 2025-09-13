from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import text

db = SQLAlchemy()
def configureDB(app):
    global db
    db.init_app(app)
    