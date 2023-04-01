import firebase_admin
from firebase_admin import credentials, firestore, storage

def firestart():
    if not firebase_admin._apps:
        cred = credentials.Certificate("static/server-assistivepro-firebase-adminsdk-mpb8d-f8b5a22e4e.json")
        app = firebase_admin.initialize_app(cred,{
            'storageBucket': "server-assistivepro.appspot.com"
        })