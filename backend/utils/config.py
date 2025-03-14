import os

class Config:
    # Database configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'cancer_db')  # Updated database name here
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    
    # Other application settings
    ITEMS_PER_PAGE = 20