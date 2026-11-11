"""Run the citation workflow from a local browser.

From the project root, set ADS_API_TOKEN and OPENAI_API_KEY, then run:
    python3.12 -m src.app
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Lock, Thread
from urllib.parse import parse_qs

from src.report import render_report, save_report
from src.workflow import summarize_citing_papers


FORM_PATH = (
    Path(__file__).resolve().parent.parent
    / "templates"
    / "run_pipeline.html"
)
run_state = {"running": False, "progress": [], "result": None, "error": None}
state_lock = Lock()


def run_pipeline(bibcode, rows):
    def record_progress(message):
        with state_lock:
            run_state["progress"].append(message)

    try:
        result = summarize_citing_papers(
            bibcode, rows=rows, progress_callback=record_progress
        )
    except Exception as exc:
        with state_lock:
            run_state["error"] = str(exc)
            run_state["running"] = False
    else:
        with state_lock:
            run_state["result"] = result
            run_state["running"] = False


class AppHandler(BaseHTTPRequestHandler):
    def send_html(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send_html(FORM_PATH.read_bytes())
        elif self.path == "/report":
            with state_lock:
                result = run_state["result"]
            if result is None:
                self.send_error(404, "No completed report is available.")
                return
            body = render_report(
                result["target"], result["citing_papers"], result["target_summary"]
            ).encode("utf-8")
            self.send_html(body)
        elif self.path == "/status":
            with state_lock:
                status = {
                    "running": run_state["running"],
                    "progress": list(run_state["progress"]),
                    "complete": run_state["result"] is not None,
                    "error": run_state["error"],
                }
            self.send_json(200, status)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/save":
            with state_lock:
                result = run_state["result"]
            if result is None:
                self.send_json(409, {"error": "There is no report to save."})
                return
            try:
                html_path, json_path = save_report(result)
            except Exception as exc:
                self.send_json(500, {"error": f"Could not save report: {exc}"})
                return
            self.send_json(200, {
                "html_path": str(html_path),
                "json_path": str(json_path),
            })
            return

        if self.path != "/run":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        bibcode = form.get("bibcode", [""])[0].strip()
        try:
            rows = int(form.get("rows", ["10"])[0])
        except ValueError:
            self.send_json(400, {"error": "Row limit must be a whole number."})
            return
        if not bibcode or rows < 1:
            self.send_json(400, {"error": "Enter a bibcode and a positive row limit."})
            return

        with state_lock:
            if run_state["running"]:
                self.send_json(409, {"error": "A run is already in progress."})
                return
            run_state.update({
                "running": True,
                "progress": [],
                "result": None,
                "error": None,
            })

        Thread(target=run_pipeline, args=(bibcode, rows), daemon=True).start()
        self.send_json(202, {"message": "Run started."})


def main():
    server = HTTPServer(("127.0.0.1", 8000), AppHandler)
    print("Open http://127.0.0.1:8000 to run the citation agent.", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
