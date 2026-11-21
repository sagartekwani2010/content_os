import json, subprocess, sys
def call(name, args=None):
    out = subprocess.run(["python3", str(__import__("pathlib").Path(__file__).resolve().parents[1] / "mcp.py"), name, json.dumps(args or {})], capture_output=True, text=True,
                         env={**__import__("os").environ, "MAXOUT": "200000"}).stdout
    d = json.loads(out); t = d["result"]["content"][0]["text"]
    try: return json.loads(t)
    except Exception: return t
if __name__ == "__main__":
    print(json.dumps(call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}), indent=1)[:4000])
