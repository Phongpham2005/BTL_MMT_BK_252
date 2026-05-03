import json
import urllib.request
from daemon import AsynapRous

peer_app = AsynapRous()
MY_USERNAME = "Phong"

@peer_app.route('/send-peer', methods=['POST'])
def receive_message(headers, body):
    """
    API lắng nghe tin nhắn trực tiếp từ một peer khác gửi tới.
    """
    try:
        data = json.loads(body)
        sender = data.get("sender")
        message = data.get("message")
        
        # Xử lý hiển thị tin nhắn lên giao diện (in ra console hoặc đẩy lên Web UI)
        print(f"\n[New message from {sender}]: {message}")
        
        return json.dumps({"status": "success"}).encode("utf-8")
    except Exception as e:
        return json.dumps({"status": "error"}).encode("utf-8")

def send_direct_message(target_ip, target_port, message):
    """
    Hàm đóng vai trò Client: Gửi HTTP POST request chứa tin nhắn đến một peer khác.
    """
    url = f"http://{target_ip}:{target_port}/send-peer"
    payload = json.dumps({"sender": MY_USERNAME, "message": message}).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"[Đã gửi]: {result}")
    except Exception as e:
        print(f"[Message failed to send]: {e}")

def run_peer_server(ip='0.0.0.0', port=8001):
    peer_app.prepare_address(ip, port)
    peer_app.run()