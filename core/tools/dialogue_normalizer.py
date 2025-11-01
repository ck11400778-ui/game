#!/usr/bin/env python3
from pathlib import Path
import json, sys

def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def normalize_dialogue(data, fname_stem):
    meta = {}
    if isinstance(data, dict) and "lines" in data:
        did = data.get("id") or fname_stem
        lines = data.get("lines", [])
        new_lines = []
        for ln in lines:
            if isinstance(ln, str):
                new_lines.append({"speaker":"", "text": ln})
            elif isinstance(ln, dict):
                new_lines.append({"speaker": ln.get("speaker",""), "text": ln.get("text","")})
            else:
                new_lines.append({"speaker":"", "text": str(ln)})
        for k,v in data.items():
            if k not in ("id","lines"):
                meta[k]=v
        out = {"id": did, "lines": new_lines}
        if meta:
            out["meta"]=meta
        return out
    if isinstance(data, dict) and len(data)==1 and isinstance(list(data.values())[0], list):
        only_key = list(data.keys())[0]
        lst = list(data.values())[0]
        new_lines = [{"speaker":"", "text": str(x)} for x in lst]
        return {"id": only_key, "lines": new_lines}
    if isinstance(data, list) and all(isinstance(x, str) for x in data):
        new_lines = [{"speaker":"", "text": x} for x in data]
        return {"id": fname_stem, "lines": new_lines}
    return {"id": fname_stem, "lines":[{"speaker":"", "text":"[Unsupported original format, see meta]"}], "meta":{"original": data}}

def main():
    root = Path(sys.argv[1]) if len(sys.argv)>1 else Path("data/dialogues")
    for p in sorted(root.glob("*.json")):
        stem = p.stem
        try:
            data = load_json(p)
            out = normalize_dialogue(data, stem)
            backup = p.with_suffix(".json.bak_pre_unify")
            if not backup.exists():
                backup.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
            p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
            print("[OK]", p)
        except Exception as e:
            print("[ERR]", p, e)

if __name__ == "__main__":
    main()
