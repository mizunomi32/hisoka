import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np

from hisoka.record import downmix, new_meeting_dir


def test_downmix():
    block = np.array([[100, 300], [-32768, -32768], [1, 2]], dtype=np.int16)
    out = downmix(block)
    assert out.dtype == np.int16
    assert out.tolist() == [200, -32768, 2]  # 平均。1.5 は偶数丸めで 2
    assert downmix(np.array([[5], [7]], dtype=np.int16)).tolist() == [5, 7]  # モノラルはそのまま


def test_new_meeting_dir():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "meetings"
        now = datetime(2026, 10, 29, 14, 0)
        assert new_meeting_dir(root, now).name == "2026-10-29_1400"
        assert new_meeting_dir(root, now).name == "2026-10-29_1400-2"


if __name__ == "__main__":
    test_downmix()
    test_new_meeting_dir()
    print("ok")
