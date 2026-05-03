import json
from daemon import AsynapRous

tracker_app = AsynapRous()

# Biến toàn cục lưu danh sách các peer đang hoạt động
# Định dạng: {"username": {"ip": "192.168.1.2", "port": 8001}}
active_peers = {}

@tracker_app.route('/submit-info', methods=['POST'])
def submit_info(headers, body):
    """
    API để peer đăng ký IP và Port khi mới online.
    """
    try:
        data = json.loads(body)
        username = data.get("username")
        ip = data.get("ip")
        port = data.get("port")
        
        active_peers[username] = {"ip": ip, "port": port}
        print(f"[Tracker] Registered peer: {username} at {ip}:{port}")
        
        response_data = {"status": "success", "message": "Registered successfully"}
        return json.dumps(response_data).encode("utf-8")
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}).encode("utf-8")

@tracker_app.route('/get-list', methods=['GET', 'POST'])
def get_list(headers, body):
    """
    API để peer lấy danh sách các peer khác đang online để chuẩn bị kết nối P2P.
    """
    response_data = {"status": "success", "peers": active_peers}
    return json.dumps(response_data).encode("utf-8")

def run_tracker(ip='0.0.0.0', port=9000):
    tracker_app.prepare_address(ip, port)
    tracker_app.run()