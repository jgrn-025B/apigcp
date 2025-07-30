import signal
import sys
from types import FrameType
import requests  # Import the requests library

from flask import Flask, jsonify  # Import jsonify for returning JSON responses
from utils.logging import logger

app = Flask(__name__)

@app.route("/<gameId>")  # Update the route to accept a gameId as a URL parameter
def fetch_game_data(gameId: str) -> str:
    """Fetch game data from Lichess and return it as JSON."""
    url = f"https://fantasy.premierleague.com/api/bootstrap-static/"  # Construct the URL with the gameId
    try:
        response = requests.get(url)  # Make a GET request to the URL
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        # Log the successful fetch
        logger.info(f"Successfully fetched data for gameId: {gameId}")

        # Return the JSON response
        return jsonify(response.json()), 200  # Return the JSON data with a 200 status code

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for gameId {gameId}: {str(e)}")
        return jsonify({"error": str(e)}), 500  # Return an error message with a 500 status code

def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")
    from utils.logging import flush
    flush()
    sys.exit(0)

if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment
    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
