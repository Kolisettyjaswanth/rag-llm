import os

from huggingface_hub import InferenceClient

from app.llm.provider import LLMProvider


class HuggingFaceProvider(LLMProvider):
    def __init__(self) -> None:
        token = os.getenv("HF_TOKEN")

        if not token:
            raise RuntimeError("HF_TOKEN is not configured")

        self.client = InferenceClient(
            api_key=token,
            provider="auto",
        )
        self.model = os.getenv(
            "HF_MODEL",
            "openai/gpt-oss-120b",
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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1200,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Hugging Face returned an empty response"
            )

        return content
