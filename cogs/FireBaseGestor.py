import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("cogs/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

db.collection("prueba").document("prueba")
firestore.Array
