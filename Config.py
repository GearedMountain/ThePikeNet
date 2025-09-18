import os
class Config:
    DEBUG = False
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://pikenet-database-owner@localhost:5433/pikenet-database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INFO_EMAIL_ADDRESS = 'noreply@gearedmountain.com'
    INFO_EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
