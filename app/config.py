import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://<dariahrychyna>:<YxczvxyKBJFpqVUo>@cluster1.pxuywoc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1')

