import asyncio
import websockets
import numpy as np
import sounddevice as sd
from transformers import pipeline

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Khởi tạo pipeline cho nhận diện giọng nói
transcriber = pipeline(
    "automatic-speech-recognition", model="vinai/PhoWhisper-tiny", device="cpu"
)

# Gửi văn bản nhận diện qua WebSocket
async def send_transcription_to_socket(result_text, websocket):
    """Gửi văn bản nhận diện qua WebSocket."""
    await websocket.send(result_text)
    print(f"Sent to WebSocket: {result_text}")

# Nhận diện giọng nói và truyền dữ liệu qua WebSocket
async def transcribe_and_stream(websocket, chunk_length_s=5.0, stream_chunk_s=0.3):
    sampling_rate = transcriber.feature_extractor.sampling_rate

    # Lấy dữ liệu âm thanh từ microphone
    mic = ffmpeg_microphone_live(
        sampling_rate=sampling_rate,
        chunk_length_s=chunk_length_s,
        stream_chunk_s=stream_chunk_s,
    )

    print("Start speaking...")
    for item in transcriber(mic):
        print(item["text"], end="\r")  # In dòng văn bản
        await send_transcription_to_socket(item["text"], websocket)

        if not item["text"]:  # Nếu không có văn bản
            break

    return item["text"]

# Lấy âm thanh từ microphone và chuyển sang dạng luồng
def ffmpeg_microphone_live(sampling_rate, chunk_length_s, stream_chunk_s):
    """Stream âm thanh từ microphone theo thời gian thực."""
    chunk_size = int(sampling_rate * chunk_length_s)
    stream_chunk_size = int(sampling_rate * stream_chunk_s)

    buffer = np.zeros((chunk_size,), dtype=np.float32)

    def callback(indata, frames, time, status):
        """Xử lý luồng âm thanh từ microphone."""
        nonlocal buffer
        if status:
            print(status)
        buffer[:-stream_chunk_size] = buffer[stream_chunk_size:]
        buffer[-stream_chunk_size:] = indata[:, 0]

    with sd.InputStream(
        samplerate=sampling_rate,
        channels=1,
        callback=callback,
        blocksize=stream_chunk_size,
        dtype=np.float32,
    ):
        while True:
            yield buffer.copy()

# Main function để kết nối WebSocket và xử lý speech-to-text
async def main():
    uri = "ws://localhost:8765"  # Địa chỉ WebSocket của server
    async with websockets.connect(uri) as websocket:
        await transcribe_and_stream(websocket)

if __name__ == "__main__":
    asyncio.run(main())
