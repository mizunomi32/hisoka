import queue
import signal
import wave
from datetime import datetime
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16000
MEETINGS_DIR = Path("meetings")


def downmix(block: np.ndarray) -> np.ndarray:
    """(フレーム数, チャンネル数) の int16 をモノラルにする。集約デバイス（マイク + BlackHole）の各チャンネルを平均する。"""
    return block.mean(axis=1).round().astype(np.int16)


def new_meeting_dir(root: Path, now: datetime) -> Path:
    """root/YYYY-MM-DD_HHMM を作る。同じ分に既にあれば -2, -3 … を付ける。"""
    base = f"{now:%Y-%m-%d_%H%M}"
    name, n = base, 1
    while (root / name).exists():
        n += 1
        name = f"{base}-{n}"
    path = root / name
    path.mkdir(parents=True)
    return path


def record(device: str | None = None, root: Path = MEETINGS_DIR) -> Path:
    """Ctrl+C を押すまで録音し、会議フォルダの audio.wav（16kHz・モノラル・16bit）に書き出す。"""
    import sounddevice as sd  # 録音しないコマンドでは PortAudio を読み込まない

    info = sd.query_devices(device, "input")
    meeting_dir = new_meeting_dir(root, datetime.now())
    blocks: queue.Queue[np.ndarray] = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        blocks.put(downmix(indata))  # 音声スレッドでは書き込まず、メインスレッドに渡す

    # Ctrl+C（SIGINT）と SIGTERM のどちらでも止めて WAV を書き切る。
    # バックグラウンドで起動されると SIGINT が無視されるため、ハンドラを明示的に入れる（メニューバーから止めるときにも使う）
    def stop(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print(f"録音中: {info['name']} → {meeting_dir / 'audio.wav'}（Ctrl+C で停止）")
    with wave.open(str(meeting_dir / "audio.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        stream = sd.InputStream(
            device=device, channels=info["max_input_channels"], samplerate=SAMPLE_RATE, dtype="int16", callback=callback
        )
        try:
            with stream:
                while True:
                    w.writeframes(blocks.get().tobytes())
        except KeyboardInterrupt:
            pass
        while not blocks.empty():  # 停止までに届いた分を書き切る
            w.writeframes(blocks.get().tobytes())
        seconds = w.getnframes() / SAMPLE_RATE
    print(f"録音停止: {seconds:.0f}秒")
    return meeting_dir
