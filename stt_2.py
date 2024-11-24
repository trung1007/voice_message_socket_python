import ffmpeg
import numpy as np
import sys
import sounddevice as sd

from transformers import pipeline

# Khởi tạo pipeline cho nhận diện giọng nói
transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-tiny", device="cpu")


def ffmpeg_microphone_live(sampling_rate, chunk_length_s, stream_chunk_s):
    """
    Ghi âm trực tiếp từ microphone và trả về stream âm thanh.
    :param sampling_rate: Tần số lấy mẫu (Hz).
    :param chunk_length_s: Độ dài mỗi chunk âm thanh (giây).
    :param stream_chunk_s: Độ dài mỗi chunk âm thanh khi stream (giây).
    :return: Generator trả về từng đoạn âm thanh.
    """
    chunk_size = int(sampling_rate * stream_chunk_s)  # Kích thước mỗi chunk âm thanh

    # Dùng ffmpeg để lấy âm thanh từ microphone
    process = (
        ffmpeg
        .input('default', format='alsa', channels=1, audio_bitrate='128k', ar=sampling_rate)
        .output('pipe:1', format='wav', acodec='pcm_s16le')
        .run_async(pipe_stdout=True)
    )

    while True:
        # Đọc một phần âm thanh từ ffmpeg stream
        in_bytes = process.stdout.read(chunk_size)

        if len(in_bytes) == 0:
            break

        # Chuyển đổi byte âm thanh thành numpy array
        audio_chunk = np.frombuffer(in_bytes, dtype=np.int16)

        yield audio_chunk

    process.stdout.close()
    process.wait()


def transcribe(chunk_length_s=5.0, stream_chunk_s=0.3):
    """
    Nhận diện giọng nói trong thời gian thực từ microphone và chuyển thành văn bản.
    :param chunk_length_s: Thời gian ghi âm mỗi đoạn (giây).
    :param stream_chunk_s: Thời gian mỗi chunk stream âm thanh (giây).
    :return: Kết quả nhận diện giọng nói.
    """
    # Lấy tần số lấy mẫu từ mô hình
    sampling_rate = transcriber.feature_extractor.sampling_rate

    # Lấy âm thanh trực tiếp từ microphone
    mic = ffmpeg_microphone_live(
        sampling_rate=sampling_rate,
        chunk_length_s=chunk_length_s,
        stream_chunk_s=stream_chunk_s,
    )

    print("Start speaking...")
    for item in transcriber(mic):
        sys.stdout.write("\033[K")
        print(item["text"], end="\r")  # Cập nhật văn bản mỗi khi nhận diện được
        if not item["partial"]:  # Nếu không còn là văn bản phụ, kết thúc
            break

    return item["text"]


# Gọi hàm để kiểm tra
if __name__ == "__main__":
    transcribed_text = transcribe()
    print(f"Final Transcription: {transcribed_text}")
