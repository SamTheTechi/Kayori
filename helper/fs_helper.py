from firebase_admin import firestore
from datetime import datetime
from util.summarize import summarizeSentence

db = firestore.client()
log_collection = db.collection("logs")


# def logger(typeof, time, error){
#
# }

print(datetime.now())
