import sounddevice as sd
import numpy as np
from transformers import pipeline
from queue import Queue

# Khởi tạo pipeline cho nhận diện giọng nói
transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small", device="cpu")

# Hàng đợi để lưu dữ liệu âm thanh
audio_queue = Queue()

def audio_callback(indata, frames, time, status):
    """
    Callback được gọi khi có dữ liệu âm thanh mới.
    :param indata: Dữ liệu âm thanh.
    :param frames: Số lượng khung hình trong đoạn âm thanh.
    :param time: Thời gian hiện tại.
    :param status: Trạng thái của stream.
    """
    if status:
        print(f"Status: {status}")
    # Đẩy dữ liệu vào hàng đợi
    audio_queue.put(indata.copy())

def process_audio_stream(sampling_rate=16000, chunk_duration=1):
    """
    Xử lý luồng âm thanh theo thời gian thực.
    :param sampling_rate: Tần số lấy mẫu (Hz).
    :param chunk_duration: Thời lượng mỗi khối (giây).
    """
    try:
        print("Listening... Speak now!")
        with sd.InputStream(callback=audio_callback, samplerate=sampling_rate, channels=1, dtype='float32', blocksize=int(sampling_rate * chunk_duration)):
            while True:
                # Kiểm tra xem có dữ liệu âm thanh mới trong hàng đợi không
                if not audio_queue.empty():
                    audio_chunk = audio_queue.get()
                    audio_flatten = audio_chunk.flatten()

                    # Gửi khối âm thanh tới mô hình nhận diện
                    print("Transcribing chunk...")
                    output = transcriber({"array": audio_flatten, "sampling_rate": sampling_rate})
                    print(f"Recognized: {output['text']}")

    except KeyboardInterrupt:
        print("Stopping the real-time transcription.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_audio_stream()
