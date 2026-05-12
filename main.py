import subprocess
import time
import webbrowser
import sys

if __name__ == "__main__":
    print("="*60)
    print("🚀 KHỞI ĐỘNG HYBRID CHAT P2P")
    print("="*60)

    try:
        # Dùng subprocess để gọi lệnh Python như khi bạn gõ trên Terminal
        print("[*] Đang khởi động Tracker (Cổng 9000)...")
        p_tracker = subprocess.Popen([sys.executable, "-c", "from apps.tracker_app import create_tracker; create_tracker('0.0.0.0', 9000)"])
        time.sleep(1) 
        
        print("[*] Đang khởi động Peer 1 (Cổng 8001)...")
        p_peer1 = subprocess.Popen([sys.executable, "-c", "from apps.peer_app import create_peer; create_peer('0.0.0.0', 8001)"])
        
        print("[*] Đang khởi động Peer 2 (Cổng 8002)...")
        p_peer2 = subprocess.Popen([sys.executable, "-c", "from apps.peer_app import create_peer; create_peer('0.0.0.0', 8002)"])

        # print("[*] Đang khởi động Peer 3 (Cổng 8003)...")
        # p_peer3 = subprocess.Popen([sys.executable, "-c", "from apps.peer_app import create_peer; create_peer('0.0.0.0', 8003)"])

        time.sleep(1.5)

        print("\n" + "="*60)
        print("✅ HỆ THỐNG ĐÃ SẴN SÀNG HOẠT ĐỘNG!")
        print("Nhấn Ctrl + Click để mở:")
        print("👉 Máy 1: http://127.0.0.1:8001/chat.html")
        print("👉 Máy 2: http://127.0.0.1:8002/chat.html")
        # print("👉 Máy 3: http://127.0.0.1:8003/chat.html")
        print("="*60 + "\n")

        # Tự động mở trình duyệt
        webbrowser.open("http://127.0.0.1:8001/chat.html")
        time.sleep(0.5)
        webbrowser.open("http://127.0.0.1:8002/chat.html")
        # time.sleep(0.5)
        # webbrowser.open("http://127.0.0.1:8003/chat.html")

        print("[!] Bấm tổ hợp phím 'Ctrl + C' để tắt toàn bộ hệ thống.")
        
        # Giữ script chạy
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Đã nhận lệnh tắt. Đang đóng các tiến trình...")
        # Tắt sạch sẽ các tiến trình con khi bấm Ctrl + C
        p_tracker.terminate()
        p_peer1.terminate()
        p_peer2.terminate()
        sys.exit(0)