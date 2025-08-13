import json, os, re, unicodedata
from typing import List, Dict, Any, Optional
try:
    from server.services.cloudinary_client import url as c_url
except ModuleNotFoundError:
    from services.cloudinary_client import url as c_url

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "recipes.json")

def _load() -> List[Dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f: return json.load(f)

def _normalize(s: str) -> str:
    s = ''.join(ch for ch in unicodedata.normalize('NFKD', s or "") if not unicodedata.combining(ch))
    s = re.sub(r"[^0-9A-Za-z\u0590-\u05FF ]+", " ", s)
    return s.lower().strip()

def _tokenize(q: str) -> List[str]:
    return [t for t in re.split(r"[,\s;]+", _normalize(q or "")) if t]

SYN: Dict[str, List[str]] = {
    "ביצה": ["ביצים"],
    "גבינה": ["גבינת"],
    "חמאה": ["מרגרינה"],
    "חלב": ["משקה חלב", "milk"],
    "בטטה": ["בטטות", "sweet potato", "sweetpotato"],
    "קינואה": ["quinoa", "קינווה"],
    "תפוח אדמה": ["תפוחי אדמה", "תפו\"א", "potato", "potatoes"],
    "טופו": ["tofu"],
    "שמן זית": ["olive oil", "שמן-זית"],
}
def _expand(tok: str) -> List[str]: return [tok] + SYN.get(tok, [])

def search_recipes(query: str, limit: int = 30, mode: str = "AND", min_k: int = 1) -> List[Dict[str, Any]]:
    items = _load(); toks = _tokenize(query)
    if not toks: return [_to_summary(r) for r in items[:limit]]

    def score(rec: Dict[str, Any]) -> int:
        title = _normalize(rec.get("title", ""))
        ingr = " ".join(_normalize(i.get("name","")) for i in rec.get("ingredients", []))
        hay = f"{title} {ingr}"
        hits = sum(1 for t in toks if any(v and v in hay for v in _expand(t)))
        ok = (mode=="AND" and hits==len(toks)) or (mode=="OR" and hits>=min_k)
        if not ok: return 0
        bonus = sum(title.count(t) for t in toks); return hits*10 + bonus

    ranked = sorted(items, key=score, reverse=True)
    return [_to_summary(r) for r in ranked if score(r)>0][:limit]

def get_recipe_by_id(rid: str) -> Optional[Dict[str, Any]]:
    for rec in _load():
        if rec.get("id")==rid: return _to_detail(rec)
    return None

def _to_summary(rec: Dict[str, Any]) -> Dict[str, Any]:
    pid = rec.get("image")
    return {"id": rec.get("id"), "title": rec.get("title"),
            "image": c_url(pid) if pid else None,
            "nutrition": rec.get("nutrition"), "tags": rec.get("tags", [])}

def _to_detail(rec: Dict[str, Any]) -> Dict[str, Any]:
    base = _to_summary(rec)
    base.update({"ingredients": rec.get("ingredients", []),
                 "steps": rec.get("steps", []),
                 "source": rec.get("source"),
                 "extra": rec.get("extra", {})})
    return base
