import firebase_admin
from firebase_admin import auth

def get_firebase_users():
    firebase_users = auth.list_users()
    print("user are ",firebase_users)
    return firebase_users
