import os
DB_NAME = "database.db"


class Config:
    SECRET_KEY = 'westly2001'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'
    # Email settings
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'admin@courses.msu.ac.zw'
    EMAIL_HOST_PASSWORD = "demc jbsb dgqi hrwf"
    EMAIL_USE_TLS = True
