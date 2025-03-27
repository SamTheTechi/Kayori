from firebase_admin import firestore, credentials
import firebase_admin
from datetime import datetime, timezone
from util.erroranalyzer import errorAnalyzer

cred = credentials.Certificate("../firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
log_collection = db.collection("logs")


def logger(typeof, error):
    analyzed_error = errorAnalyzer(error)
    error_cleaned = str(analyzed_error.replace('"', "'"))
    log_collection.add({
        "root": typeof,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description": error_cleaned
    })
