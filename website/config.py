class Config:
    
    SECRET_KEY = "your_secret_key"
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mydatabase.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    LOGIN_VIEW = 'login'
    
class DevelopmentConfig(Config):
    DEBUG = True
    