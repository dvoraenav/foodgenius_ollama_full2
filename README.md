# FoodGenius — Full Stack (FastAPI + PySide6) with Ollama AI

## Start
### Server
```
cd server
python -m venv .venv && (.venv\Scripts\activate || source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env   # או copy ב-Windows
uvicorn main:app --reload
```
### Client
```
cd client
python -m venv .venv && (.venv\Scripts\activate || source .venv/bin/activate)
pip install -r requirements.txt
python main.py
```
### Ollama
```
ollama serve
ollama pull llama3
```
