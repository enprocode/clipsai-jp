import os
import sys
import types
from unittest.mock import MagicMock

# リサイズ/話者分離の依存が無い環境でも clip 系テストを実行できるようにする。
# CI でフル依存が入っている場合は何もしない。


def _stub_package(name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__path__ = []  # type: ignore[attr-defined]
    sys.modules[name] = mod
    return mod


try:
    import cv2  # noqa: F401
except ImportError:
    sys.modules["cv2"] = MagicMock()

try:
    import mediapipe  # noqa: F401
except ImportError:
    sys.modules["mediapipe"] = MagicMock()

try:
    import scenedetect  # noqa: F401
except ImportError:
    sd = types.ModuleType("scenedetect")
    sd.detect = MagicMock()
    sd.AdaptiveDetector = MagicMock()
    sys.modules["scenedetect"] = sd

try:
    from pyannote.audio import Pipeline  # noqa: F401
    from pyannote.core.annotation import Annotation  # noqa: F401
except ImportError:
    _stub_package("pyannote")
    audio = _stub_package("pyannote.audio")
    audio.Pipeline = MagicMock()
    core = _stub_package("pyannote.core")
    annotation = types.ModuleType("pyannote.core.annotation")
    annotation.Annotation = MagicMock()
    sys.modules["pyannote.core.annotation"] = annotation
    core.annotation = annotation

sys.path.insert(0, os.path.abspath("clipsai"))
