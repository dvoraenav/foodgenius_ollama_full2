import json, os, re
SUBS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "substitutions.json")
def _load_subs():
    try:
        with open(os.path.abspath(SUBS_PATH), "r", encoding="utf-8") as f: return json.load(f)
    except FileNotFoundError: return {}
def veganize(recipe: dict) -> dict:
    subs = _load_subs(); replaced=[]; new_ing=[]
    animal_terms = {"ביצה","חמאה","חלב","גבינה","גבינת","עוף","בשר","דג","דגים","שמנת"}
    for i in recipe.get("ingredients", []):
        name = i.get("name","")
        if any(term in name for term in animal_terms):
            key = next((term for term in animal_terms if term in name), None)
            options = subs.get(key or "", [])
            if options:
                swapped = options[0].get("name", "תחליף צמחי")
                replaced.append({"from": name, "to": swapped})
                new_ing.append({"name": swapped})
            else:
                replaced.append({"from": name, "to": None, "note": "אין תחליף במאגר"})
        else:
            new_ing.append(i)
    return {"title": recipe.get("title","")+" (גרסה טבעונית)","ingredients": new_ing,
            "steps": recipe.get("steps", []),"replacements": replaced}
def scale(recipe: dict, factor: float) -> dict:
    def scale_amount(txt: str):
        if not isinstance(txt, str): return txt
        m = re.search(r"([0-9]+(?:\\.[0-9]+)?)", txt or "")
        if not m: return txt
        num = float(m.group(1)); new = round(num*factor,2)
        return txt.replace(m.group(1), str(new))
    new_ing=[]; 
    for i in recipe.get("ingredients", []):
        i2 = dict(i)
        if "amount" in i2 and isinstance(i2["amount"], str):
            i2["amount"] = scale_amount(i2["amount"])
        new_ing.append(i2)
    return {"title": recipe.get("title",""),"ingredients": new_ing,"steps": recipe.get("steps", [])}
