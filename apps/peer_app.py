import json
import os
import urllib.parse
import urllib.request
from daemon import AsynapRous

app = AsynapRous()
my_username = ""
message_history = []

DB_DIR = "json"
DB_FILE = os.path.join(DB_DIR, "users.json")


def load_db():

    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    if not os.path.exists(DB_FILE): 

        default_db = {"admin": "123"}
        save_db(default_db)
        return default_db
        
    with open(DB_FILE, "r", encoding="utf-8") as f: 
        return json.load(f)

def save_db(db):
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    with open(DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(db, f, indent=4) 

users_db = load_db()

@app.route('/register', methods=['POST'])
def register(headers, body):
    params = urllib.parse.parse_qs(body)
    u, p = params.get("username", [""])[0], params.get("password", [""])[0]
    db = load_db()
    if u in db: return {"status": "error", "message": "Account exists!"}
    db[u] = p
    save_db(db)
    return {"status": "success"}

@app.route('/login', methods=['POST'])
def login(headers, body):
    global my_username
    params = urllib.parse.parse_qs(body)
    u, p = params.get("username", [""])[0], params.get("password", [""])[0]
    db = load_db()

    # 1. Check credentials
    if db.get(u) != p:
        return {"status": "error", "message": "Invalid credentials!"}

    # 2. Check if already Online via Tracker
    try:
        with urllib.request.urlopen("http://127.0.0.1:9000/get-list") as resp:
            data = json.loads(resp.read().decode())
            if u in data.get("peers", {}):
                return {"status": "error", "message": "This account is already logged in elsewhere!"}
    except: pass # If tracker is down, allow local login

    my_username = u
    return {"status": "success"}

@app.route('/logout', methods=['POST'])
def logout(headers, body):
    global my_username
    my_username = ""
    return {"status": "success"}

@app.route('/broadcast-peer', methods=['POST'])
def broadcast_peer(headers, body):
    data = json.loads(body)
    message_history.append({"sender": data.get("sender"), "message": data.get("message"), "type": "broadcast", "channel": data.get("channel")})
    return {"status": "success"}

@app.route('/send-broadcast', methods=['POST'])
def api_send_broadcast(headers, body):
    data = json.loads(body)
    msg, channel = data.get("message"), data.get("channel", "Global")
    try:
        with urllib.request.urlopen("http://127.0.0.1:9000/get-list") as resp:
            t_data = json.loads(resp.read().decode())
            online_peers = t_data["peers"]
            chan_info = t_data["channels"].get(channel, {})
            members, is_private = chan_info.get("members", []), chan_info.get("is_private", False)

        for name, info in online_peers.items():
            if name != my_username and (not is_private or name in members):
                p2p_url = f"http://{info['ip']}:{info['port']}/broadcast-peer"
                p_data = json.dumps({"sender": my_username, "message": msg, "channel": channel}).encode()
                urllib.request.urlopen(urllib.request.Request(p2p_url, data=p_data, method='POST'))
        
        message_history.append({"sender": my_username, "message": msg, "type": "broadcast", "channel": channel})
        return {"status": "success"}
    except: return {"status": "error"}

@app.route('/get-messages', methods=['GET'])
def get_messages(headers, body):
    return {"messages": message_history}

def create_peer(ip, port):
    app.prepare_address(ip, port); app.run()