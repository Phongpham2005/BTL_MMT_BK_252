import json
import urllib.request
from daemon import AsynapRous

app = AsynapRous()

my_username = ""
message_history = []

@app.route('/login', methods=['POST'])
def login(headers, body):
    global my_username
    data = json.loads(body)
    my_username = data.get("username")
    return {"status": "success"}

@app.route('/connect-peer', methods=['POST'])
def connect_peer(headers, body):
    data = json.loads(body)
    peer_name = data.get("peer_name")
    print(f"\n[P2P] Connection established with {peer_name}")
    return {"status": "success", "message": "Connected"}

@app.route('/send-peer', methods=['POST'])
def send_peer(headers, body):
    data = json.loads(body)
    sender = data.get("sender")
    message_history.append({
        "sender": sender, 
        "message": data.get("message"), 
        "type": "direct",
        "channel": "Private" # Đánh dấu là tin nhắn riêng
    })
    return {"status": "success"}

@app.route('/broadcast-peer', methods=['POST'])
def broadcast_peer(headers, body):
    data = json.loads(body)
    sender = data.get("sender")
    channel = data.get("channel", "Global")
    msg = data.get("message")
    
    # Lưu rõ tên kênh (channel) vào lịch sử
    message_history.append({
        "sender": sender, 
        "message": msg, 
        "type": "broadcast",
        "channel": channel
    })
    return {"status": "success"}

@app.route('/api/send-broadcast', methods=['POST'])
def api_send_broadcast(headers, body):
    data = json.loads(body)
    msg = data.get("message")
    channel = data.get("channel", "Global")
    tracker_url = "http://127.0.0.1:9000/get-list" 
    
    try:
        import urllib.request
        req = urllib.request.Request(tracker_url, method='GET')
        with urllib.request.urlopen(req) as response:
            tracker_data = json.loads(response.read().decode())
            peers = tracker_data["peers"]
            channels_info = tracker_data["channels"]
            
        # Lấy danh sách những người được cấp quyền trong kênh này
        authorized_members = channels_info.get(channel, {}).get("members", [])
            
        for peer_name, info in peers.items():
            # Access Control: Chỉ gửi nếu peer đó nằm trong danh sách authorized_members
            if peer_name != my_username and (channel == "Global" or peer_name in authorized_members): 
                p2p_url = f"http://{info['ip']}:{info['port']}/broadcast-peer"
                payload = json.dumps({
                    "sender": my_username, 
                    "message": msg, 
                    "channel": channel
                }).encode('utf-8')
                
                p2p_req = urllib.request.Request(p2p_url, data=payload, method='POST')
                urllib.request.urlopen(p2p_req) 
                
        message_history.append({"sender": my_username, "message": msg, "type": "broadcast", "channel": channel})
        return {"status": "success"}
    except Exception as e:
        print(f"Broadcast Error: {e}")
        return {"status": "error"}

@app.route('/get-messages', methods=['GET'])
def get_messages(headers, body):
    return {"messages": message_history}

def create_peer(ip, port):
    app.prepare_address(ip, port)
    app.run()