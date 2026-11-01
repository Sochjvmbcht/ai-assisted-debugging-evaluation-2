"""Small standard-library client for Ollama's local chat API."""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from typing import Any

class OllamaError(RuntimeError):
    pass

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:3b", timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _request(self, endpoint: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{endpoint}", data=data,
            headers={"Content-Type": "application/json"} if data is not None else {},
            method="GET" if data is None else "POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OllamaError(f"Ollama HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise OllamaError(f"Cannot reach Ollama at {self.base_url}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise OllamaError("Ollama returned invalid JSON.") from exc

    def ensure_model(self) -> None:
        """Fail early with a useful message instead of writing misleading failed rows."""
        response = self._request("/api/tags")
        installed = [item.get("name", "") for item in response.get("models", [])]
        if self.model not in installed and f"{self.model}:latest" not in installed:
            choices = ", ".join(installed) if installed else "none found"
            raise OllamaError(f"Model '{self.model}' is not installed. Installed models: {choices}. Run: ollama pull {self.model}")

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, *, json_mode: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model, "messages": messages, "stream": False,
            "keep_alive": "5m",
            "options": {"temperature": 0, "num_ctx": 2048, "num_predict": 180},
        }
        if tools:
            payload["tools"] = tools
        if json_mode:
            payload["format"] = "json"
        return self._request("/api/chat", payload)
