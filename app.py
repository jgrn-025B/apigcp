import signal
import sys
from types import FrameType
import requests
from flask import Flask, jsonify
from utils.logging import logger
from google.cloud import storage

app = Flask(__name__)

@app.route("/")
def fetch_data() -> str:
    # Use basic logging with custom fields
    logger.info(logField="custom-entry", arbitraryField="custom-entry")

    # Fetch data from the URL
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)

    if response.status_code == 200:
        # Log the successful fetch
        logger.info("Data fetched successfully from the URL.")
        
        # Optionally, you can upload the data to Google Cloud Storage
        upload_to_gcs(response.json())

        return jsonify(response.json())
    else:
        logger.error(f"Failed to fetch data: {response.status_code}")
        return jsonify({"error": "Failed to fetch data"}), response.status_code

def upload_to_gcs(data):
    # Initialize a Cloud Storage client
    client = storage.Client()
    bucket = client.bucket("my_bucket_jgrn")
    blob = bucket.blob("data.json")

    # Upload the JSON data to the bucket
    blob.upload_from_string(data=json.dumps(data), content_type='application/json')
    logger.info("Data uploaded to Google Cloud Storage.")

def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")
    from utils.logging import flush
    flush()
    # Safely exit program
    sys.exit(0)

if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment
    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
