
import httpx

async def ollama_generate(prompt: str, system: str = "", temperature: float = 0.3) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "system": system,
        "temperature": temperature,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()["response"]
