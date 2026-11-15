import os, sys, json, urllib.request
URL = "http://127.0.0.1:19501/mcp"
TOK = os.environ.get("METAPILOT_TOKEN") or os.popen("launchctl getenv METAPILOT_TOKEN").read().strip()
SID = None
def rpc(method, params=None, notify=False):
    global SID
    body = {"jsonrpc": "2.0", "method": method}
    if params is not None: body["params"] = params
    if not notify: body["id"] = 1
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "Authorization": "Bearer " + TOK}
    if SID: h["Mcp-Session-Id"] = SID
    r = urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode(), h), timeout=600)
    SID = r.headers.get("Mcp-Session-Id") or SID
    raw = r.read().decode()
    if notify or not raw.strip(): return None
    if raw.lstrip().startswith("{"): return json.loads(raw)
    out = None
    for line in raw.splitlines():
        if line.startswith("data:"):
            out = json.loads(line[5:])
    return out
def init():
    rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "cli", "version": "1"}})
    rpc("notifications/initialized", notify=True)
def call(name, args):
    return rpc("tools/call", {"name": name, "arguments": args})
if __name__ == "__main__":
    init()
    if sys.argv[1] == "list":
        for t in rpc("tools/list")["result"]["tools"]:
            print("##", t["name"], "-", (t.get("description") or "")[:300].replace("\n", " "))
            print("   ", json.dumps(t.get("inputSchema", {}).get("properties", {}))[:600])
    else:
        print(json.dumps(call(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}), indent=1)[:int(os.environ.get("MAXOUT", "6000"))])
