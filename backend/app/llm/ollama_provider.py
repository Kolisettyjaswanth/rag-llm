import json
import os
import urllib.request

from app.llm.provider import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434",
        )
        self.model = os.getenv(
            "OLLAMA_MODEL",
            "llama3.1:8b",
        )

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "stream": False,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result["message"]["content"]