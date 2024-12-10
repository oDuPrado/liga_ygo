import firebase_admin
from firebase_admin import credentials, firestore

# Caminho para o arquivo JSON de credenciais
cred = credentials.Certificate("credentials/ygo-app-bc-firebase-adminsdk-ybxk9-5ac70bf166.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
