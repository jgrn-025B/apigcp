import signal
import sys
import json
import requests
from types import FrameType
from flask import Flask, request
from google.cloud import storage
from utils.logging import logger, flush

app = Flask(__name__)

def remove_empty_structs(obj):
    """Recursively remove empty dicts and None values from JSON."""
    if isinstance(obj, dict):
        return {
            k: remove_empty_structs(v)
            for k, v in obj.items()
            if v not in (None, {}, []) and remove_empty_structs(v) != {}
        }
    elif isinstance(obj, list):
        return [remove_empty_structs(item) for item in obj if item not in (None, {}, [])]
    else:
        return obj

@app.route("/", methods=["GET"])
def fetch_and_store():
    logger.info(logField="custom-entry", arbitraryField="custom-entry")
    logger.info("Child logger with trace Id.")

    try:
        game_id = request.args.get("gameId")
        if not game_id:
            return "Missing gameId query parameter", 400

        url = f"https://lichess.org/game/export/{game_id}"
        response = requests.get(url)
        response.raise_for_status()
        pgn_text = response.text

        # Save PGN to a temporary file
        temp_pgn_path = f"/tmp/{game_id}.pgn"
        with open(temp_pgn_path, "w", encoding="utf-8") as f:
            f.write(pgn_text)

        # Convert PGN to CSV using PGNData
        from converter.pgn_data import PGNData
        pgn_data = PGNData(temp_pgn_path)
        csv_path = pgn_data.export()  # Assuming export() returns the CSV file path

        # Upload CSV to Cloud Storage
        client = storage.Client()
        bucket = client.bucket("my_bucket_jgrn")
        blob = bucket.blob(f"{game_id}.csv")
        with open(csv_path, "rb") as csv_file:
            blob.upload_from_file(csv_file, content_type="text/csv")

        return "CSV uploaded to Cloud Storage", 200

    except Exception as e:
        logger.error(f"Error during fetch and store: {str(e)}")
        return f"Error: {str(e)}", 500
    
def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")
    flush()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(host="localhost", port=8080, debug=True)
else:
    signal.signal(signal.SIGTERM, shutdown_handler)
