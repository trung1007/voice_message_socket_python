from flask import Flask, request
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép CORS cho tất cả các origin

# Biến toàn cục để lưu trữ văn bản mới nhất nhận được
received_text = ""

@app.route('/receive_text', methods=['POST'])
def receive_text():
    """
    Nhận văn bản từ client và phát dữ liệu đến tất cả các client kết nối.
    """
    global received_text
    # Lấy văn bản từ form POST request
    text = request.form.get('text')

    if text:
        received_text = text  # Lưu văn bản
        print(f"Received text: {text}")
        
        # Phát dữ liệu đến tất cả các client đang kết nối
        socketio.emit('update_text', {
            "received_text": received_text,
            "timestamp": time.time()
        })
        return "Text received", 200

    return "No text received", 400

@socketio.on('connect')
def on_connect():
    """
    Xử lý sự kiện client kết nối.
    """
    print("A client connected.")
    
    # Khi client kết nối, nếu đã có dữ liệu nhận, gửi ngay lập tức
    if received_text:
        emit('update_text', {
            "received_text": received_text,
            "timestamp": time.time()
        })

@socketio.on('disconnect')
def on_disconnect():
    """
    Xử lý sự kiện client ngắt kết nối.
    """
    print("A client disconnected.")
    received_text = ""  # Đặt lại giá trị của received_text
    print(receive_text)
    socketio.emit('update_text', {
        "received_text": None,  # Gửi cập nhật để client biết dữ liệu đã bị xóa
        "timestamp": time.time()
    })

if __name__ == "__main__":
    # Chạy server với Socket.IO
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
