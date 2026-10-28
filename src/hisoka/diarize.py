import json
import tarfile
import urllib.request
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

MODELS_DIR = Path.home() / ".cache" / "hisoka" / "models"
RELEASES = "https://github.com/k2-fsa/sherpa-onnx/releases/download"
SEGMENTATION_URL = f"{RELEASES}/speaker-segmentation-models/sherpa-onnx-pyannote-segmentation-3-0.tar.bz2"
EMBEDDING_URL = f"{RELEASES}/speaker-recongition-models/3dspeaker_speech_eres2net_base_sv_zh-cn_3dspeaker_16k.onnx"


def _download(url: str) -> Path:
    dest = MODELS_DIR / url.rsplit("/", 1)[1]
    if not dest.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.rename(dest)
    return dest


def _models() -> tuple[Path, Path]:
    """初回のみ GitHub Releases からモデルを取得し、(segmentation, embedding) のパスを返す。"""
    segmentation = MODELS_DIR / "sherpa-onnx-pyannote-segmentation-3-0" / "model.onnx"
    if not segmentation.exists():
        with tarfile.open(_download(SEGMENTATION_URL)) as tar:
            tar.extractall(MODELS_DIR, filter="data")
    return segmentation, _download(EMBEDDING_URL)


def _read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path)) as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2, "16bit モノラルの WAV が必要"
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        return pcm.astype(np.float32) / 32768, w.getframerate()


def diarize(meeting_dir: Path, num_speakers: int | None = None) -> Path:
    """meeting_dir/audio.wav を話者分離し、meeting_dir/diarization.json に書き出す。"""
    segmentation, embedding = _models()
    config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=str(segmentation)),
            num_threads=4,
        ),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(embedding), num_threads=4),
        # 人数不明のときは距離のしきい値でクラスタ数を決める
        clustering=sherpa_onnx.FastClusteringConfig(num_clusters=num_speakers or -1, threshold=0.5),
    )
    sd = sherpa_onnx.OfflineSpeakerDiarization(config)

    samples, rate = _read_wav(meeting_dir / "audio.wav")
    assert rate == sd.sample_rate, f"{sd.sample_rate}Hz の WAV が必要"
    result = sd.process(samples).sort_by_start_time()

    turns = [{"start": t.start, "end": t.end, "speaker": t.speaker} for t in result]
    out = meeting_dir / "diarization.json"
    out.write_text(json.dumps(turns, ensure_ascii=False, indent=2))
    return out
