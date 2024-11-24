import tkinter as tk
from tkinter import messagebox
import requests
import time
import threading

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Client - Receive Data from Server")

        # Khởi tạo một nút để bắt đầu nhận dữ liệu từ server
        self.start_button = tk.Button(root, text="Nhận Dữ Liệu", command=self.start_receiving, bg="green", fg="white")
        self.start_button.pack(pady=20)

        # Khung hiển thị kết quả
        self.result_label = tk.Label(root, text="Kết quả sẽ hiển thị ở đây", wraplength=400, justify="center")
        self.result_label.pack(pady=20)

    def start_receiving(self):
        """Bắt đầu nhận dữ liệu từ server khi nhấn nút."""
        self.start_button.config(state="disabled")  # Vô hiệu hóa nút khi đã nhấn
        self.result_label.config(text="Đang nhận dữ liệu từ server...")

        # Chạy hàm fetch_data_from_server trong một thread để không làm treo giao diện
        threading.Thread(target=self.fetch_data_from_server, daemon=True).start()

    def fetch_data_from_server(self):
        """Lấy dữ liệu từ server mỗi 5 giây."""
        server_url = "http://localhost:5000/send_data"
        while True:
            try:
                # Gửi yêu cầu GET đến server để lấy dữ liệu
                response = requests.get(server_url)

                # Kiểm tra nếu yêu cầu thành công (status code 200)
                if response.status_code == 200:
                    # Hiển thị dữ liệu nhận được từ server
                    data = response.json()
                    print(f"Received data: {data}")
                    self.update_label(f"Received data: {data}")
                else:
                    self.update_label(f"Failed to retrieve data. Status code: {response.status_code}")

            except Exception as e:
                print(f"Error fetching data: {e}")
                self.update_label("Lỗi khi kết nối server")

            # Chờ 5 giây trước khi gửi yêu cầu tiếp theo
            time.sleep(5)

    def update_label(self, text):
        """Cập nhật nội dung hiển thị trên label."""
        self.result_label.config(text=text)

# Tạo giao diện Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
