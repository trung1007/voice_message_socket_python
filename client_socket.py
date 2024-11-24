import tkinter as tk
import sounddevice as sd
import numpy as np
from transformers import pipeline
import threading
import queue
import requests  # For sending HTTP requests

# Khởi tạo pipeline cho nhận diện giọng nói
transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-tiny", device="cpu")

class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recorder and Transcriber (Real-time)")
        self.recording = False
        self.sampling_rate = 16000
        self.audio_queue = queue.Queue()  # Hàng đợi lưu trữ dữ liệu âm thanh
        self.result_text = ""  # Kết quả nhận diện
        self.volume_threshold = 0.02  # Ngưỡng âm thanh tối thiểu để bắt đầu nhận diện

        # Nút bắt đầu ghi âm
        self.start_button = tk.Button(root, text="Bắt đầu ghi âm", command=self.start_recording, bg="green", fg="white")
        self.start_button.pack(pady=10)

        # Nút dừng ghi âm
        self.stop_button = tk.Button(root, text="Dừng ghi âm", command=self.stop_recording, bg="red", fg="white", state="disabled")
        self.stop_button.pack(pady=10)

        # Khung hiển thị kết quả
        self.result_label = tk.Label(root, text="Kết quả sẽ hiển thị ở đây", wraplength=400, justify="center")
        self.result_label.pack(pady=20)

    def start_recording(self):
        """Bắt đầu ghi âm và nhận diện theo thời gian thực."""
        self.recording = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        # Luồng ghi âm
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()

        # Luồng xử lý nhận diện
        self.transcribing_thread = threading.Thread(target=self.transcribe_audio)
        self.transcribing_thread.start()

    def stop_recording(self):
        """Dừng ghi âm và quá trình nhận diện."""
        self.recording = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def record_audio(self):
        """Ghi âm và lưu dữ liệu vào hàng đợi."""
        print("Bắt đầu ghi âm...")
        try:
            while self.recording:
                # Ghi âm từng đoạn nhỏ (0.5 giây)
                audio = sd.rec(int(self.sampling_rate * 5), samplerate=self.sampling_rate, channels=1, dtype='float32')
                sd.wait()

                # Kiểm tra âm lượng (ngưỡng)
                if np.max(np.abs(audio)) > self.volume_threshold:
                    self.audio_queue.put(audio.flatten())  # Đưa dữ liệu âm thanh vào hàng đợi
        except Exception as e:
            print(f"Lỗi khi ghi âm: {e}")
        print("Dừng ghi âm.")

    def transcribe_audio(self):
        """Lấy dữ liệu từ hàng đợi và nhận diện giọng nói."""
        while self.recording or not self.audio_queue.empty():
            try:
                audio_chunk = self.audio_queue.get(timeout=1)  # Lấy dữ liệu âm thanh từ hàng đợi
                output = transcriber({"array": audio_chunk, "sampling_rate": self.sampling_rate})
                self.result_text += output['text'] + " "  # Thêm kết quả nhận diện vào chuỗi
                print(f"{self.result_text}")
                self.result_label.config(text=f"Kết quả: {self.result_text}")

                # Gửi kết quả lên server sau mỗi lần nhận diện
                self.send_to_server(self.result_text)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Lỗi khi nhận diện: {e}")
                break
        print("Dừng nhận diện.")

    def send_to_server(self, result_text):
        """Gửi kết quả nhận diện lên server thông qua HTTP."""
        try:
            # URL của server (cập nhật lại theo server của bạn)
            server_url = "http://localhost:5000/receive_text"  # Ví dụ URL server nhận dữ liệu

            # Dữ liệu cần gửi
            data = {'text': result_text}

            # Gửi POST request
            response = requests.post(server_url, data=data)

            # Kiểm tra phản hồi từ server
            if response.status_code == 200:
                print("Dữ liệu đã được gửi thành công!")
            else:
                print(f"Lỗi khi gửi dữ liệu: {response.status_code}")
        except Exception as e:
            print(f"Lỗi khi gửi dữ liệu lên server: {e}")


# Tạo ứng dụng Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceRecorderApp(root)
    root.mainloop()
