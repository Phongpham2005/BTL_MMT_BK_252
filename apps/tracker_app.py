import json
import os
from daemon import AsynapRous

app = AsynapRous()
active_peers = {} 
CHANNELS_FILE = os.path.join("json", "channels.json")

def load_channels():
    if not os.path.exists("json"): os.makedirs("json")
    if not os.path.exists(CHANNELS_FILE):
        return {"Global": {"password": "", "members": [], "creator": "System"}}
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_channels(data):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

active_channels = load_channels()

@app.route('/add-list', methods=['POST'])
def add_list(headers, body):
    data = json.loads(body)
    name, password, creator = data.get("channel_name"), data.get("password", ""), data.get("creator")
    if name and name not in active_channels:
  
        active_channels[name] = {"password": password, "members": [creator], "creator": creator}
        save_channels(active_channels)
        return {"status": "success"}
    return {"status": "error", "message": "Channel already exists!"}

@app.route('/delete-channel', methods=['POST'])
def delete_channel(headers, body):
    data = json.loads(body)
    u, name = data.get("username"), data.get("channel_name")
    if name in active_channels and name != "Global":

        if active_channels[name].get("creator") == u:
            del active_channels[name]
            save_channels(active_channels)
            print(f"[Tracker] Channel {name} deleted by creator {u}")
            return {"status": "success"}
    return {"status": "error", "message": "Unauthorized or channel not found"}

@app.route('/get-list', methods=['GET'])
def get_list(headers, body):
    safe_ch = {ch: {
        "is_private": bool(info["password"]), 
        "members": info["members"],
        "creator": info.get("creator", "") 
    } for ch, info in active_channels.items()}
    return {"status": "success", "peers": active_peers, "channels": safe_ch}


@app.route('/submit-info', methods=['POST'])
def submit_info(headers, body):
    data = json.loads(body); u = data.get("username")
    active_peers[u] = {"ip": data.get("ip"), "port": data.get("port")}
    if u not in active_channels["Global"]["members"]:
        active_channels["Global"]["members"].append(u); save_channels(active_channels)
    return {"status": "success"}

@app.route('/unregister', methods=['POST'])
def unregister(headers, body):
    try:

        if body:
            data = json.loads(body)
            u = data.get("username")
            if u and u in active_peers: 
                del active_peers[u]
                print(f"[Tracker] User {u} logged out successfully.")
    except Exception as e:
        print(f"[Tracker] Unregister error: {e}")
        
    return {"status": "success"}

@app.route('/join-channel', methods=['POST'])
def join_channel(headers, body):
    data = json.loads(body); u, name, pwd = data.get("username"), data.get("channel_name"), data.get("password", "")
    if name in active_channels:
        ch = active_channels[name]
        if u in ch["members"] or ch["password"] == "" or ch["password"] == pwd:
            if u not in ch["members"]: ch["members"].append(u); save_channels(active_channels)
            return {"status": "success"}
        return {"status": "error", "message": "Invalid password!"}
    return {"status": "error", "message": "Channel not found!"}

@app.route('/leave-channel', methods=['POST'])
def leave_channel(headers, body):
    data = json.loads(body); u, name = data.get("username"), data.get("channel_name")
    if name in active_channels and name != "Global":
        if u in active_channels[name]["members"]:
            active_channels[name]["members"].remove(u); save_channels(active_channels)
            return {"status": "success"}
    return {"status": "error"}

def create_tracker(ip, port):
    try:
        app.prepare_address(ip, port)
        app.run()
    except KeyboardInterrupt:
        print("\n[Tracker] Server stopped by user request.")