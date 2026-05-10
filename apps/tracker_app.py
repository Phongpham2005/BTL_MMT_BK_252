import json
from daemon import AsynapRous

app = AsynapRous()

active_peers = {}
# Cấu trúc mới: Lưu mật khẩu và danh sách thành viên đã được duyệt
active_channels = {
    "Global": {"password": "", "members": []} 
}

@app.route('/submit-info', methods=['POST'])
def submit_info(headers, body):
    data = json.loads(body)
    username = data.get("username")
    active_peers[username] = {"ip": data.get("ip"), "port": data.get("port")}
    print(f"[Tracker] Peer {username} joined.")
    return {"status": "success"}

@app.route('/add-list', methods=['POST'])
def add_list(headers, body):
    data = json.loads(body)
    channel_name = data.get("channel_name")
    password = data.get("password", "")
    creator = data.get("creator")

    if channel_name and channel_name not in active_channels:
        # Khởi tạo kênh mới, thêm luôn người tạo vào danh sách members
        active_channels[channel_name] = {"password": password, "members": [creator]}
        print(f"[Tracker] Tạo kênh: {channel_name} (Private: {bool(password)})")
        return {"status": "success"}
    return {"status": "error", "message": "Channel already exists!"}

@app.route('/join-channel', methods=['POST'])
def join_channel(headers, body):
    """API mới để kiểm tra quyền truy cập (Access Control)"""
    data = json.loads(body)
    username = data.get("username")
    channel_name = data.get("channel_name")
    password = data.get("password", "")

    if channel_name in active_channels:
        ch_info = active_channels[channel_name]
        # Kiểm tra chính sách truy cập: Kênh public hoặc mật khẩu phải đúng
        if ch_info["password"] == "" or ch_info["password"] == password:
            if username not in ch_info["members"]:
                ch_info["members"].append(username)
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Incorrect access password!"}
    return {"status": "error", "message": "Channel does not exist!"}

@app.route('/get-list', methods=['GET'])
def get_list(headers, body):
    # Ẩn mật khẩu thực sự trước khi gửi cho các Peer để bảo mật
    safe_channels = {}
    for ch, info in active_channels.items():
        safe_channels[ch] = {
            "is_private": bool(info["password"]),
            "members": info["members"]
        }
    return {"status": "success", "peers": active_peers, "channels": safe_channels}

def create_tracker(ip, port):
    app.prepare_address(ip, port)
    app.run()