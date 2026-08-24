import json, sqlite3, sys, os
from pathlib import Path

db = Path(r"c:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\data\gabriel_repo_map.db")
print("DB exists:", db.exists(), "| size:", db.stat().st_size if db.exists() else 0)
if db.exists():
    c = sqlite3.connect(str(db))
    print("TABLES:", [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")])
    for t in ["files", "file_edges", "snapshots"]:
        try:
            n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  count[{t}] = {n}")
        except Exception as e:
            print(f"  error {t}: {e}")
    try:
        print("\nSample files rows:")
        for r in c.execute("SELECT rel_path, role, score FROM files LIMIT 8"):
            print("   ", r)
        print("\nSample edges rows:")
        for r in c.execute("SELECT src_path, dst_path, relation FROM file_edges LIMIT 8"):
            print("   ", r)
        print("\nSnapshots rows:")
        for r in c.execute("SELECT id, repo_root, total_files, total_edges FROM snapshots"):
            print("   ", r)
    except Exception as e:
        print("query err", e)

summ = Path(r"c:\agent-multiloop-Gabriel-local-final\agent-multiloop-Gabriel-local\data\gabriel_repo_summary.json")
print("\nSummary exists:", summ.exists())
if summ.exists():
    import json
    d = json.loads(summ.read_text(encoding="utf-8"))
    print(json.dumps({k: v for k, v in d.items() if k not in ("extra",)}, ensure_ascii=False, indent=2)[:2000])