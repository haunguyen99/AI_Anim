"""Goi mot tool MCP cua Frolvy theo cong: python3 -I mcp_call.py <cong> <tool> '<json args>' | 'list' """
import subprocess, json, os, sys
port, tool = sys.argv[1], sys.argv[2]
args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
env = dict(os.environ, DCC_MCP_PORT=port)
p = subprocess.Popen([os.path.expanduser('~/.local/share/frolvy/Frolvy-mcp')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
def s(m): p.stdin.write((json.dumps(m) + "\n").encode()); p.stdin.flush()
def r(i):
    while True:
        m = json.loads(p.stdout.readline())
        if m.get('id') == i: return m
s({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "x", "version": "1"}}}); r(1)
s({"jsonrpc": "2.0", "method": "notifications/initialized"})
if tool == 'schema':
    s({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    for t in r(2)['result']['tools']:
        if t['name'] == args.get('name'): print(json.dumps(t, indent=1)[:3000])
else:
    s({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": args}})
    res = r(2).get('result')
    print("\n".join(c.get('text', '') for c in res['content']) if res and 'content' in res else res)
p.kill()
