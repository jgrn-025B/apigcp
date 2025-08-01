# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import flask
from flask.testing import FlaskClient
import requests


def test_system(app: flask.app.Flask, client: FlaskClient) -> None:

    BASE_URL = os.environ.get("BASE_URL")
    assert BASE_URL, "Cloud Run service URL not found"

    ID_TOKEN = os.environ.get("ID_TOKEN")
    assert ID_TOKEN, "Unable to acquire an ID token"

    resp = requests.get(BASE_URL, headers={"Authorization": f"Bearer {ID_TOKEN}"})
    assert resp.status_code == 200
    assert resp.text == "Hello, World From Test System!"
