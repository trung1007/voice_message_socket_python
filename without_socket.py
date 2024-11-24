from transformers import pipeline
import sounddevice as sd
import numpy as np

# Khởi tạo pipeline cho nhận diện giọng nói
transcriber = pipeline(
    "automatic-speech-recognition", model="vinai/PhoWhisper-base", device="cpu"
)

def sounddevice_microphone_live(sampling_rate, chunk_length_s, stream_chunk_s):
    """Stream âm thanh từ microphone theo thời gian thực bằng sounddevice."""
    chunk_size = int(sampling_rate * chunk_length_s)  # Số mẫu cho mỗi chunk
    stream_chunk_size = int(sampling_rate * stream_chunk_s)

    buffer = np.zeros((chunk_size,), dtype=np.float32)

    def callback(indata, frames, time, status):
        """Xử lý luồng âm thanh từ microphone."""
        nonlocal buffer
        if status:
            print(status)
        buffer[:-stream_chunk_size] = buffer[stream_chunk_size:]
        buffer[-stream_chunk_size:] = indata[:, 0]  # Chỉ lấy kênh âm thanh đầu tiên

    with sd.InputStream(
        samplerate=sampling_rate,
        channels=1,  # Ghi âm mono
        callback=callback,
        blocksize=stream_chunk_size,
        dtype=np.float32,
    ):
        while True:
            yield buffer.copy()

def transcribe_and_print(chunk_length_s=5.0, stream_chunk_s=0.3):
    """Nhận diện giọng nói từ microphone và in kết quả."""
    sampling_rate = transcriber.feature_extractor.sampling_rate

    mic = sounddevice_microphone_live(
        sampling_rate=sampling_rate,
        chunk_length_s=chunk_length_s,
        stream_chunk_s=stream_chunk_s,
    )

    print("Start speaking...")
    for item in transcriber(mic):
        print(f"Transcription: {item['text']}")  # In văn bản nhận diện
        if not item["text"]:  # Nếu không có văn bản
            break

if __name__ == "__main__":
    # Chạy chức năng nhận diện giọng nói và in kết quả
    transcribe_and_print()
