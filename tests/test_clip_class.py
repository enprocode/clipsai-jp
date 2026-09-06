"""Clip クラスの真偽値・等価性のテスト"""

from clipsai_jp.clip.clip import Clip


def test_opening_clip_is_truthy():
    """start_time=0 / start_char=0 の冒頭クリップは真。"""
    clip = Clip(start_time=0.0, end_time=30.0, start_char=0, end_char=40)
    assert bool(clip) is True
    assert clip


def test_empty_clip_is_falsy():
    assert bool(Clip(0.0, 0.0, 0, 0)) is False
    assert bool(Clip(10.0, 10.0, 5, 5)) is False


def test_reversed_clip_is_falsy():
    assert bool(Clip(30.0, 10.0, 40, 0)) is False
    assert bool(Clip(0.0, 30.0, 40, 0)) is False


def test_mid_video_clip_is_truthy():
    clip = Clip(start_time=120.0, end_time=150.0, start_char=80, end_char=200)
    assert bool(clip) is True
