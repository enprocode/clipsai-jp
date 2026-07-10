"""
char_info の時間区間の不変条件（ソート済み・非重複）に関するテスト

- Transcriber._enforce_monotonic_char_info が重なり/逆転を補正すること
- Transcription._find_index が None 時刻に対して明確なエラーを出すこと
"""

import pytest

from clipsai_jp.transcribe.transcriber import Transcriber
from clipsai_jp.transcribe.transcription import Transcription
from clipsai_jp.transcribe.exceptions import TranscriptionError


def _times(char_info):
    return [(c["start_time"], c["end_time"]) for c in char_info]


def test_enforce_monotonic_fixes_overlap():
    """隣接区間が重なる場合、後続の start_time が直前の end_time にクランプされる"""
    char_info = [
        {"char": "a", "start_time": 0.0, "end_time": 1.0, "speaker": None},
        # 前の文字(end=1.0)と重なる start=0.5
        {"char": "b", "start_time": 0.5, "end_time": 1.5, "speaker": None},
    ]
    Transcriber._enforce_monotonic_char_info(char_info)
    assert _times(char_info) == [(0.0, 1.0), (1.0, 1.5)]


def test_enforce_monotonic_fixes_reversed_interval():
    """end_time < start_time の逆転区間は end_time = start_time に補正される"""
    char_info = [
        {"char": "a", "start_time": 2.0, "end_time": 1.0, "speaker": None},
    ]
    Transcriber._enforce_monotonic_char_info(char_info)
    assert _times(char_info) == [(2.0, 2.0)]


def test_enforce_monotonic_result_is_sorted_nonoverlapping():
    """補正後は必ずソート済み・非重複（start[i] >= end[i-1], start <= end）"""
    char_info = [
        {"char": "a", "start_time": 0.0, "end_time": 1.0, "speaker": None},
        {"char": "b", "start_time": 0.2, "end_time": 0.8, "speaker": None},
        {"char": "c", "start_time": 0.9, "end_time": 0.5, "speaker": None},
        {"char": "d", "start_time": 3.0, "end_time": 4.0, "speaker": None},
    ]
    Transcriber._enforce_monotonic_char_info(char_info)
    prev_end = None
    for c in char_info:
        assert c["start_time"] <= c["end_time"]
        if prev_end is not None:
            assert c["start_time"] >= prev_end
        prev_end = c["end_time"]


def test_enforce_monotonic_skips_none_times():
    """None 時刻の要素はスキップし、他要素の補正を妨げない"""
    char_info = [
        {"char": "a", "start_time": 0.0, "end_time": 1.0, "speaker": None},
        {"char": " ", "start_time": None, "end_time": None, "speaker": None},
        {"char": "b", "start_time": 0.5, "end_time": 1.5, "speaker": None},
    ]
    Transcriber._enforce_monotonic_char_info(char_info)
    assert char_info[1]["start_time"] is None
    # None を挟んでも直前の実時刻(1.0)基準でクランプされる
    assert char_info[2]["start_time"] == 1.0


def _make_transcription(char_info):
    data = {
        "source_software": "faster-whisper",
        "time_created": "2026-07-11 00:00:00.000000",
        "language": "ja",
        "num_speakers": None,
        "char_info": char_info,
    }
    return Transcription(data)


def test_find_index_raises_clear_error_on_none_time():
    """None 時刻を含む char_info で時間検索すると TranscriptionError になる"""
    char_info = [
        {"char": "a", "start_time": 0.0, "end_time": 1.0, "speaker": None},
        {"char": "b", "start_time": None, "end_time": None, "speaker": None},
        {"char": "c", "start_time": 2.0, "end_time": 3.0, "speaker": None},
    ]
    transcription = _make_transcription(char_info)
    with pytest.raises(TranscriptionError):
        transcription.find_char_index(1.5, type_of_time="start")
