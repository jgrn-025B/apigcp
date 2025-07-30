import signal
import sys
from types import FrameType
import requests  # Import the requests library
import chess.pgn  # Import the python-chess library
import json  # Import json for JSON serialization

from flask import Flask, Response, jsonify  # Import Response and jsonify
from utils.logging import logger

app = Flask(__name__)

@app.route("/<gameId>")  # Update the route to accept a gameId as a URL parameter
def fetch_game_data(gameId: str) -> Response:
    """Fetch game data from Lichess in PGN format, convert to JSON, and return it."""
    url = f"https://lichess.org/study/KZ4GGtvY/BUMkRuMO"  # Construct the URL with the gameId
    try:
        response = requests.get(url)  # Make a GET request to the URL
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        # Log the successful fetch
        logger.info(f"Successfully fetched PGN data for gameId: {gameId}")

        # Parse the PGN data
        pgn_data = response.text
        game = chess.pgn.read_game(io.StringIO(pgn_data))  # Read the PGN data

        # Convert the game to a dictionary
        game_dict = {
            "headers": game.headers,
            "moves": [move.san() for move in game.mainline_moves()]
        }

        # Return the JSON response
        return jsonify(game_dict), 200  # Return the game data as JSON with a 200 status code

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data for gameId {gameId}: {str(e)}")
        return Response(f"Error fetching data: {str(e)}", status=500, mimetype='text/plain')  # Return error message as plain text

    except Exception as e:
        logger.error(f"Error processing PGN data for gameId {gameId}: {str(e)}")
        return Response(f"Error processing PGN data: {str(e)}", status=500, mimetype='text/plain')  # Return error message as plain text

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
