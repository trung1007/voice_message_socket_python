import asyncio
import websockets
from transformers import pipeline
import sounddevice as sd
import numpy as np

# Khởi tạo pipeline cho nhận diện giọng nói
transcriber = pipeline(
    "automatic-speech-recognition", model="vinai/PhoWhisper-base", device="cpu"
)

async def send_transcription_to_socket(result_text, websocket):
    """Gửi văn bản nhận diện qua WebSocket."""
    await websocket.send(result_text)
    print(f"Sent to WebSocket: {result_text}")

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

async def transcribe_and_stream(websocket, chunk_length_s=5.0, stream_chunk_s=0.3):
    sampling_rate = transcriber.feature_extractor.sampling_rate

    mic = sounddevice_microphone_live(
        sampling_rate=sampling_rate,
        chunk_length_s=chunk_length_s,
        stream_chunk_s=stream_chunk_s,
    )

    print("Start speaking...")
    for item in transcriber(mic):
        print(item["text"], end="\r")  # In dòng văn bản

        # Gửi văn bản nhận diện qua WebSocket
        await send_transcription_to_socket(item["text"], websocket)

        if not item["text"]:  # Nếu không có văn bản
            break

    return item["text"]

async def main():
    uri = "ws://localhost:8765"  # Địa chỉ WebSocket của server

    async with websockets.connect(uri) as websocket:
        # Bắt đầu nhận diện giọng nói và gửi dữ liệu lên WebSocket
        await transcribe_and_stream(websocket)

if __name__ == "__main__":
    # Chạy WebSocket client để gửi dữ liệu lên server
    asyncio.run(main())
