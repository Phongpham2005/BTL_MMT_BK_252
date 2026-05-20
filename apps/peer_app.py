import json
import os
import threading
import urllib.parse
import urllib.request
import time
from daemon import AsynapRous
from datetime import datetime

app = AsynapRous()
my_username = ""
message_history = []
network_cache = {"peers": {}, "channels": {}}
# --- THREAD LOCK ---
peer_locks = {}
peer_locks_lock = threading.Lock()

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
    if not body or body.strip() == "":
        return {"status": "error", "message": "Empty body"}
        
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format"}
    data = json.loads(body)
    current_time = datetime.now().strftime("%H:%M")
    
    message_history.append({
        "sender": data.get("sender"), 
        "message": data.get("message"), 
        "type": "broadcast", 
        "channel": data.get("channel"),
        "time": current_time 
    })
    return {"status": "success"}

def get_peer_lock(peer_name):
    with peer_locks_lock:
        if peer_name not in peer_locks:
            peer_locks[peer_name] = threading.Lock()
        return peer_locks[peer_name]

# 1. Hàm vận chuyển P2P 
def p2p_send_task(p2p_url, p_data, target_name):
    lock = get_peer_lock(target_name)
    with lock:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(p2p_url, data=p_data, method='POST')
                with urllib.request.urlopen(req, timeout=2) as resp:
                    if resp.getcode() == 200:
                        return 
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))

# 2. Hàm định tuyến chạy ngầm
def routing_task(msg, channel, sender_username):
    global network_cache
    
    try:
        with urllib.request.urlopen("http://127.0.0.1:9000/get-list", timeout=1) as resp:
            network_cache = json.loads(resp.read().decode())
    except Exception:
        pass 
            
    online_peers = network_cache.get("peers", {})
    chan_info = network_cache.get("channels", {}).get(channel, {})
    members = chan_info.get("members", [])
    is_private = chan_info.get("is_private", False)

    for name, info in online_peers.items():
        if name != sender_username:
            if channel == "Global" or not is_private or name in members:
                p2p_url = f"http://{info['ip']}:{info['port']}/broadcast-peer"
                p_data = json.dumps({"sender": sender_username, "message": msg, "channel": channel}).encode()
                t = threading.Thread(target=p2p_send_task, args=(p2p_url, p_data, name))
                t.daemon = True
                t.start()


# API ĐỒNG BỘ LỊCH SỬ TIN NHẮN
@app.route('/sync-history', methods=['POST'])
def api_sync_history(headers, body):
    global message_history
 
    if len(message_history) > 0:
        return {"status": "skipped", "reason": "History already exists"}
        
    try:
        with urllib.request.urlopen("http://127.0.0.1:9000/get-list", timeout=1) as resp:
            data = json.loads(resp.read().decode())
            peers = data.get("peers", {})
            
            for name, info in peers.items():
                if name != my_username:
                    try:

                        url = f"http://{info['ip']}:{info['port']}/get-messages"
                        with urllib.request.urlopen(url, timeout=1.5) as p_resp:
                            p_data = json.loads(p_resp.read().decode())
                            if p_data.get("messages"):
                                message_history = p_data.get("messages")
                                return {"status": "success", "synced_from": name}
                    except Exception:
                        continue 
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    return {"status": "success", "message": "No other online peers found to sync from"}

@app.route('/send-broadcast', methods=['POST'])
def api_send_broadcast(headers, body):
    data = json.loads(body)
    msg, channel = data.get("message"), data.get("channel", "Global")
    current_time = datetime.now().strftime("%H:%M") 

    t_route = threading.Thread(target=routing_task, args=(msg, channel, my_username))
    t_route.daemon = True
    t_route.start()

    message_history.append({
        "sender": my_username, 
        "message": msg, 
        "type": "broadcast", 
        "channel": channel,
        "time": current_time
    })
    
    return {"status": "success"}

@app.route('/get-messages', methods=['GET'])
def get_messages(headers, body):
    return {"messages": message_history}

@app.route('/clear-messages', methods=['POST'])
def api_clear_messages(headers, body):
    data = json.loads(body)
    channel_to_clear = data.get("channel")
    global message_history
    
    if channel_to_clear:
        message_history = [m for m in message_history if m.get("channel") != channel_to_clear]
        
    return {"status": "success"}

def background_cache_updater():
    global network_cache
    while True:
        try:
            with urllib.request.urlopen("http://127.0.0.1:9000/get-list", timeout=1) as resp:
                network_cache = json.loads(resp.read().decode())
        except Exception:
            pass 
        time.sleep(2)

def create_peer(ip, port):
    t_cache = threading.Thread(target=background_cache_updater)
    t_cache.daemon = True
    t_cache.start()
    
    app.prepare_address(ip, port)
    app.run()