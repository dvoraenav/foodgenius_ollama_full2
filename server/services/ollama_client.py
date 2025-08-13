import os, httpx
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

async def ollama_generate(prompt: str, system: str | None = None, temperature: float = 0.2) -> str:
    payload = {
        "model": OLLAMA_MODEL,
       "prompt": f"{system + chr(10) if system else ''}{prompt}",


        "stream": False,
        "options": {"temperature": temperature}
    }
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        r.raise_for_status()
        return (r.json().get("response") or "").strip()
