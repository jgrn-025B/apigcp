import json
import requests
from google.cloud import storage
import functions_framework

@functions_framework.http
def fetch_and_store(request):
    """Fetch data from the API and store it in Google Cloud Storage."""
    try:
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Initialize Cloud Storage client
        client = storage.Client()
        bucket = client.bucket("my_bucket_jgrn")  # Replace with your actual bucket name
        blob = bucket.blob("fpl_data.json")
        blob.upload_from_string(data=json.dumps(data), content_type="application/json")

        return "Data uploaded to Cloud Storage", 200

    except requests.exceptions.RequestException as e:
        return f"Error fetching data from API: {str(e)}", 500
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
