import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "my-private-key")

    SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False  