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
        # Implement a simple PGN to CSV conversion here as PGNData is not available
        import csv

        def pgn_to_csv(pgn_path, csv_path):
            with open(pgn_path, "r", encoding="utf-8") as pgn_file, open(csv_path, "w", newline='', encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Event", "Site", "Date", "Round", "White", "Black", "Result", "Moves"])
                event, site, date, round_, white, black, result, moves = "", "", "", "", "", "", "", ""
                for line in pgn_file:
                    if line.startswith("[Event "):
                        event = line.split('"')[1]
                    elif line.startswith("[Site "):
                        site = line.split('"')[1]
                    elif line.startswith("[Date "):
                        date = line.split('"')[1]
                    elif line.startswith("[Round "):
                        round_ = line.split('"')[1]
                    elif line.startswith("[White "):
                        white = line.split('"')[1]
                    elif line.startswith("[Black "):
                        black = line.split('"')[1]
                    elif line.startswith("[Result "):
                        result = line.split('"')[1]
                    elif line.strip() and not line.startswith("["):
                        moves = line.strip()
                writer.writerow([event, site, date, round_, white, black, result, moves])

        csv_path = f"/tmp/{game_id}.csv"
        pgn_to_csv(temp_pgn_path, csv_path)

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
