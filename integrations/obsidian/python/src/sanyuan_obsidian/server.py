from __future__ import annotations

import hmac
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .pipeline import ContextPipeline
from .providers import should_retrieve


class SidecarServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        pipeline: ContextPipeline,
        token: str | None = None,
    ):
        super().__init__(server_address, SidecarHandler)
        self.pipeline = pipeline
        self.token = token or ""


class SidecarHandler(BaseHTTPRequestHandler):
    server: SidecarServer
    protocol_version = "HTTP/1.1"
    max_body_bytes = 1_048_576

    def log_message(self, format: str, *args: object) -> None:
        # Avoid logging queries or response bodies. The endpoint and status remain visible.
        path = self.path.split("?", 1)[0]
        self.server.pipeline  # keep a typed server access without exposing request data
        print(f"sanyuan-sidecar {self.command} {path}")

    def _authorized(self) -> bool:
        if not self.server.token:
            return True
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {self.server.token}"
        return hmac.compare_digest(supplied, expected)

    def _json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length <= 0 or length > self.max_body_bytes:
            raise ValueError("request body is empty or too large")
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("request body must be UTF-8 JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("request body must be a JSON object")
        return data

    def do_GET(self) -> None:
        if not self._authorized():
            self._json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return
        if self.path == "/health":
            self._json(HTTPStatus.OK, self.server.pipeline.health())
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "not-found"})

    def do_POST(self) -> None:
        if not self._authorized():
            self._json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return
        try:
            payload = self._read_json()
            query = str(payload.get("query", ""))
            if self.path == "/v1/should-retrieve":
                decision, reason = should_retrieve(query)
                self._json(
                    HTTPStatus.OK,
                    {"query": query, "should_retrieve": decision, "reason": reason},
                )
                return
            if self.path != "/v1/retrieve-and-inject":
                self._json(HTTPStatus.NOT_FOUND, {"error": "not-found"})
                return
            axes_value = payload.get("query_axes")
            query_axes = (
                [str(axis) for axis in axes_value]
                if isinstance(axes_value, list)
                else None
            )
            result = self.server.pipeline.retrieve_and_inject(
                query,
                top_k=int(payload.get("top_k", 8)),
                mode=str(payload.get("mode", "full")),
                trigger_policy=str(payload.get("trigger_policy", "always")),
                query_axes=query_axes,
                current_path=(
                    str(payload["current_path"])
                    if payload.get("current_path")
                    else None
                ),
            )
            self._json(HTTPStatus.OK, result.to_dict())
        except (TypeError, ValueError) as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except RuntimeError as exc:
            self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(exc)})


def serve(
    pipeline: ContextPipeline,
    host: str = "127.0.0.1",
    port: int = 8765,
    token: str | None = None,
) -> None:
    server = SidecarServer((host, port), pipeline, token=token)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
