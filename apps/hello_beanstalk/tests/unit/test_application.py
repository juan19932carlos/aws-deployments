import importlib.util
import json
from pathlib import Path

# application.py is a top-level module at the app root (EB requires it there),
# not an installed package, so load it by path.
_spec = importlib.util.spec_from_file_location(
    "application", Path(__file__).parents[2] / "application.py"
)
application = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(application)


def test_application_returns_json():
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(application.application({}, start_response))

    assert captured["status"] == "200 OK"
    assert captured["headers"]["Content-Type"] == "application/json"
    # The text changes between deploys; only its type is part of the contract.
    assert isinstance(json.loads(body)["message"], str)
