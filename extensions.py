import os
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
class Config:
    SECRET_KEY =  os.getenv('SECRET_KEY','clave1234')
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:8673.l@localhost:5432/modelo'
    SQLALCHEMY_TRACK_MODIFICATIONS = False