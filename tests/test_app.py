"""Test the local browser app without contacting ADS or OpenAI."""

import json
from http.server import HTTPServer
from threading import Event, Thread
from time import monotonic, sleep
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src import app


def test_app_runs_workflow_and_serves_report(monkeypatch):
    results = {
        "target": {
            "bibcode": "TARGET",
            "title": "Target paper",
            "author": ["Doe, Jane"],
            "year": "2025",
        },
        "target_summary": {"summary": "Target summary", "metadata": None},
        "citing_papers": [],
    }
    workflow_finished = Event()
    calls = []

    def fake_workflow(bibcode, rows, progress_callback):
        calls.append((bibcode, rows))
        progress_callback("Fetched target record.")
        workflow_finished.set()
        return results

    monkeypatch.setattr(app, "summarize_citing_papers", fake_workflow)
    monkeypatch.setitem(app.run_state, "running", False)
    monkeypatch.setitem(app.run_state, "progress", [])
    monkeypatch.setitem(app.run_state, "result", None)
    monkeypatch.setitem(app.run_state, "error", None)

    server = HTTPServer(("127.0.0.1", 0), app.AppHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(f"{base_url}/") as response:
            assert b'name="bibcode"' in response.read()

        try:
            urlopen(f"{base_url}/report")
        except HTTPError as error:
            assert error.code == 404
        else:
            raise AssertionError("Report route should be unavailable before a run")

        request = Request(
            f"{base_url}/run",
            data=urlencode({"bibcode": "TARGET", "rows": "3"}).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urlopen(request) as response:
            assert response.status == 202
            assert json.load(response) == {"message": "Run started."}

        assert workflow_finished.wait(2)
        deadline = monotonic() + 2
        while monotonic() < deadline:
            with urlopen(f"{base_url}/status") as response:
                status = json.load(response)
            if status["complete"]:
                break
            sleep(0.01)

        assert calls == [("TARGET", 3)]
        assert status == {
            "running": False,
            "progress": ["Fetched target record."],
            "complete": True,
            "error": None,
        }
        with urlopen(f"{base_url}/report") as response:
            assert response.status == 200
            assert "Target paper" in response.read().decode("utf-8")
    finally:
        server.shutdown()
        server_thread.join()
        server.server_close()
