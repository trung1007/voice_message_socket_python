from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# To store the latest received text
received_text = ""

@app.route('/receive_text', methods=['POST'])
def receive_text():
    """
    Lấy văn bản gửi từ client và lưu trữ nó.
    :return: Phản hồi khi nhận được văn bản.
    """
    global received_text  # Use the global variable to store the text
    # Lấy văn bản gửi từ client
    text = request.form.get('text')

    if text:
        received_text = text  # Store the received text
        print(f"Received text: {text}")  # In kết quả nhận từ client
        return "Text received", 200  # Trả về phản hồi thành công
    return "No text received", 400  # Trả về phản hồi lỗi nếu không có text

@app.route("/send_data", methods=["GET"])
def send_data():
    """
    Gửi dữ liệu đến client, chỉ khi có văn bản đã nhận từ /receive_text.
    :return: Dữ liệu JSON gửi tới client hoặc thông báo lỗi nếu chưa có dữ liệu.
    """
     # Kiểm tra xem văn bản đã nhận hay chưa
    if not received_text:
        return '', 204  # Không trả gì, chỉ trả về mã trạng thái 204 (No Content)

    # Nếu đã có văn bản, gửi dữ liệu
    data = {
        "message": "Hello from server",
        "received_text": received_text,  # Thêm văn bản đã nhận
        "timestamp": time.time()
    }
    return jsonify(data)  # Gửi dữ liệu dưới dạng JSON đến client


if __name__ == "__main__":
    # Chạy server trên địa chỉ localhost và cổng 5000
    app.run(debug=True, host="0.0.0.0", port=5000)
