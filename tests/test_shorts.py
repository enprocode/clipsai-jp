"""
ショート動画向けクリップ候補生成・スコアリング・重複抑制のテスト
"""

from unittest.mock import MagicMock, patch

import pytest
import torch

from clipsai_jp.clip.clipfinder import ClipFinder
from clipsai_jp.clip.gemini_clipfinder import GeminiClipFinder
from clipsai_jp.clip.shorts import (
    clip_iou,
    generate_sentence_windows,
    is_shorts_mode,
    rank_and_suppress,
    score_clip_text,
    snap_clip_to_sentences,
)


def _sentences():
    """0秒から10文×6秒 = 60秒のダミー文"""
    texts = [
        "プログラミングやってみたいんだけど、何から始めればいい？",
        "まずは目的を決めましょう。",
        "そして次に言語を選びます。",
        "Pythonは初心者におすすめです。",
        "一方でJavaScriptはWeb向きです。",
        "挫折しないコツは毎日5分触れることです。",
        "2つ目はエラーを恐れないこと。",
        "3つ目はコミュニティで共有すること。",
        "さて、ここまで一緒に見てくれてありがとうございます。",
        "このお話が最高に嬉しいです。是非チャンネル登録を。",
    ]
    info = []
    t = 0.0
    char = 0
    for text in texts:
        end_char = char + len(text)
        info.append(
            {
                "sentence": text,
                "start_time": t,
                "end_time": t + 6.0,
                "start_char": char,
                "end_char": end_char,
            }
        )
        t += 6.0
        char = end_char
    return info


def test_is_shorts_mode_auto_uses_max_duration():
    assert is_shorts_mode("auto", 60) is True
    assert is_shorts_mode("auto", 900) is False
    assert is_shorts_mode("shorts", 900) is True
    assert is_shorts_mode("longform", 30) is False


def test_generate_sentence_windows_respects_duration():
    windows = generate_sentence_windows(_sentences(), 12, 24)
    assert windows
    for w in windows:
        dur = w["end_time"] - w["start_time"]
        assert 12 <= dur <= 24


def test_score_prefers_hook_over_cta():
    hook = score_clip_text(
        "プログラミングやってみたいんだけど、何から始めればいい？まずは目的を決めましょう。",
        32.0,
        10,
        60,
    )
    cta = score_clip_text(
        "さて、ここまで一緒に見てくれてありがとうございます。このお話が最高に嬉しいです。",
        32.0,
        10,
        60,
    )
    continuation = score_clip_text(
        "一方でJavaScriptはWeb向きです。Pythonは初心者におすすめです。",
        32.0,
        10,
        60,
    )
    assert hook > cta
    assert hook > continuation


def test_score_boosts_opening_hook():
    text = "プログラミングやってみたいんだけど、何から始めればいい？まずは目的を決めましょう。"
    opening = score_clip_text(text, 28.0, 10, 60, start_time=0.0)
    later = score_clip_text(text, 28.0, 10, 60, start_time=120.0)
    assert opening > later
    sweet = score_clip_text(
        "なぜPythonがおすすめなのか。理由は文法が簡単だからです。", 35.0, 10, 60
    )
    too_short = score_clip_text(
        "なぜPythonがおすすめなのか。理由は文法が簡単だからです。", 12.0, 10, 60
    )
    assert sweet > too_short


def test_clip_iou_and_rank_suppresses_overlap():
    text = "".join(s["sentence"] for s in _sentences())
    sents = _sentences()
    overlapping = [
        {
            "start_time": sents[0]["start_time"],
            "end_time": sents[4]["end_time"],
            "start_char": sents[0]["start_char"],
            "end_char": sents[4]["end_char"],
        },
        {
            "start_time": sents[1]["start_time"],
            "end_time": sents[5]["end_time"],
            "start_char": sents[1]["start_char"],
            "end_char": sents[5]["end_char"],
        },
        {
            "start_time": sents[5]["start_time"],
            "end_time": sents[7]["end_time"],
            "start_char": sents[5]["start_char"],
            "end_char": sents[7]["end_char"],
        },
    ]
    assert clip_iou(0, 30, 6, 36) > 0.45
    kept = rank_and_suppress(overlapping, text, 10, 60, overlap_threshold=0.45)
    assert len(kept) == 2
    # 先頭フックを含む候補が残る
    first_text = text[kept[0]["start_char"] : kept[0]["end_char"]]
    assert "プログラミングやってみたい" in first_text or "挫折" in first_text


def test_snap_clip_to_sentence_boundaries():
    sents = _sentences()
    clip = {
        "start_time": 1.5,  # 1文目の途中
        "end_time": 10.0,  # 2文目の途中
        "start_char": 3,
        "end_char": 20,
    }
    snapped = snap_clip_to_sentences(clip, sents)
    assert snapped["start_time"] == sents[0]["start_time"]
    assert snapped["end_time"] == sents[1]["end_time"]
    assert snapped["start_char"] == sents[0]["start_char"]
    assert snapped["end_char"] == sents[1]["end_char"]


def test_clip_finder_defaults_to_japanese_embedding():
    finder = ClipFinder(device="cpu")
    assert finder._embedding_model == "japanese"
    assert finder._clip_style == "auto"
    assert finder._max_clips is None


def test_clip_finder_rejects_invalid_clip_style():
    with pytest.raises(Exception):
        ClipFinder(device="cpu", clip_style="viral")


def test_text_tile_does_not_reuse_boundary_sentence():
    """境界文を次クリップ先頭に二重含めない"""
    sentences = [
        {
            "sentence": f"文{i}。",
            "start_char": i * 3,
            "end_char": i * 3 + 2,
            "start_time": float(i),
            "end_time": float(i) + 1,
        }
        for i in range(6)
    ]
    embeddings = torch.ones(6, 4)
    finder = ClipFinder(device="cpu")
    mock_tiler = MagicMock()
    mock_tiler.text_tile.return_value = (
        [0, 0, 1, 0, 0, 1],
        torch.ones(2, 4),
    )
    with patch("clipsai_jp.clip.clipfinder.TextTiler", return_value=mock_tiler):
        super_clips, _ = finder._text_tile(sentences, embeddings, k=3)

    assert len(super_clips) == 2
    # 1つ目は文0-2、2つ目は文3-5。文2を共有しない
    assert super_clips[0]["end_char"] == sentences[2]["end_char"]
    assert super_clips[1]["start_char"] == sentences[3]["start_char"]
    assert super_clips[0]["end_time"] == 3.0
    assert super_clips[1]["start_time"] == 3.0


def test_gemini_shorts_prompt_mentions_hooks():
    prompt = GeminiClipFinder._build_prompt(
        "プレビュー",
        [{"index": 0, "start_time": 0, "end_time": 5, "sentence": "こんにちは。"}],
        10,
        60,
        for_shorts=True,
    )
    assert "YouTubeショート" in prompt
    assert "フック" in prompt
    longform = GeminiClipFinder._build_prompt(
        "プレビュー",
        [{"index": 0, "start_time": 0, "end_time": 5, "sentence": "こんにちは。"}],
        10,
        60,
        for_shorts=False,
    )
    assert "トピック境界" in longform
