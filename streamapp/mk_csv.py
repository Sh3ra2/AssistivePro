import csv
import firebase_admin
from firebase_admin import credentials, firestore, storage, db

# <-------------- Accessing database -------------->
if not firebase_admin._apps:
    cred = credentials.Certificate("static/server-assistivepro-firebase-adminsdk-mpb8d-f8b5a22e4e.json")
    app = firebase_admin.initialize_app(cred,{
        'databaseURL': "https://server-assistivepro-default-rtdb.firebaseio.com/",
	    'storageBucket': "server-assistivepro.appspot.com"
	})
# bucket = storage.bucket()
db = firestore.client()

def export_firestore_to_csv(collection_name, filename):
   
    # Get a reference to the collection
    collection_ref = db.collection(collection_name)

    # Get all documents in the collection
    docs = collection_ref.stream()


    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)

        # Write the header row to the CSV file
        writer.writerow(['id'])
        # Iterate over each document in the collection
        for doc in docs:
            # Get the document data as a dictionary
            print("-------- file to write is ",doc)
            data = doc.to_dict()
            writer.writerow([data['id']])
            # print(data)
        # print(data)

# export_firestore_to_csv('recent_att', f'media/att_data/data.csv')

