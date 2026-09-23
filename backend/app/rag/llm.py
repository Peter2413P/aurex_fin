import os
import json
import requests
from typing import Generator

class OllamaLLM:
    """
    Direct, lightweight Ollama client providing invoke() and stream() methods
    with zero langchain_community import overhead and high reliability.
    """
    def __init__(self, model: str = None, temperature: float = 0.1, base_url: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.temperature = temperature
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def invoke(self, prompt: str) -> str:
        try:
            url = f"{self.base_url.rstrip('/')}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature
                }
            }
            res = requests.post(url, json=payload, timeout=60)
            if res.status_code == 200:
                data = res.json()
                return data.get("response", "")
            return ""
        except Exception as e:
            print(f"[OllamaLLM] invoke error: {e}")
            return ""

    def stream(self, prompt: str) -> Generator[str, None, None]:
        try:
            url = f"{self.base_url.rstrip('/')}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": self.temperature
                }
            }
            res = requests.post(url, json=payload, stream=True, timeout=60)
            if res.status_code == 200:
                for line in res.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        chunk = data.get("response", "")
                        if chunk:
                            yield chunk
        except Exception as e:
            print(f"[OllamaLLM] stream error: {e}")
            return

def get_llm() -> OllamaLLM:
    return OllamaLLM(
        model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        temperature=0.1
    )
