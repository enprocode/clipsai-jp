"""
ショート動画向けクリップ候補生成・スコアリング・重複抑制のテスト
"""

from unittest.mock import MagicMock, patch

import pytest
import torch

from clipsai_jp.clip.clipfinder import ClipFinder
from clipsai_jp.clip.llm_clipfinder import LlmClipFinder
from clipsai_jp.clip.shorts import (
    MAX_GENERATED_WINDOWS,
    OPENING_PRIORITY_START,
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


def test_generate_sentence_windows_is_bounded_for_long_transcripts():
    """長尺・細かい文分割でも候補辞書を上限以内に抑える。"""
    sentences = []
    t = 0.0
    char = 0
    for i in range(4000):
        text = f"文{i}。"
        sentences.append(
            {
                "sentence": text,
                "start_time": t,
                "end_time": t + 0.5,
                "start_char": char,
                "end_char": char + len(text),
            }
        )
        t += 0.5
        char += len(text)
    windows = generate_sentence_windows(sentences, 10, 60)
    assert windows
    assert len(windows) <= MAX_GENERATED_WINDOWS
    assert any(w["start_time"] <= OPENING_PRIORITY_START for w in windows)
    last_quarter = sentences[-1]["end_time"] * 0.75
    assert any(w["start_time"] >= last_quarter for w in windows)
    for w in windows:
        assert 10 <= w["end_time"] - w["start_time"] <= 60


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


def test_score_opening_hook_beats_numbered_advice():
    """冒頭の問いかけフックは、中盤の番号付きアドバイスより高くなる。"""
    opening = score_clip_text(
        "プログラミングやってみたいんだけど、何から始めればいい？まずは目的を決めましょう。",
        32.0,
        10,
        60,
        start_time=0.0,
    )
    advice = score_clip_text(
        "1つ目はコピーすること。2つ目は検索すること。3つ目は毎日触れることです。",
        32.0,
        10,
        60,
        start_time=200.0,
    )
    assert opening > advice


def test_rank_reserves_opening_hook_in_top_clips():
    """中盤の非重複アドバイスが多数でも、冒頭フックを1枠残す。"""
    opening_text = "プログラミングやってみたいんだけど、何から始めればいい？"
    advice_text = "1つ目はこれ。2つ目はあれ。3つ目はそれです。"
    parts = [opening_text]
    clips = [
        {
            "start_time": 0.0,
            "end_time": 30.0,
            "start_char": 0,
            "end_char": len(opening_text),
        }
    ]
    cursor = len(opening_text)
    # 8本の非重複アドバイス（開始は15秒より後）
    for i in range(8):
        start = 40.0 + i * 35.0
        clips.append(
            {
                "start_time": start,
                "end_time": start + 30.0,
                "start_char": cursor,
                "end_char": cursor + len(advice_text),
            }
        )
        parts.append(advice_text)
        cursor += len(advice_text)

    kept = rank_and_suppress(clips, "".join(parts), 10, 60, max_clips=8)
    assert len(kept) == 8
    assert any(clip["start_time"] == 0.0 for clip in kept)


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


def test_snap_does_not_cross_silence_gap_into_previous_topic():
    """無音ギャップ上の開始は次の文頭へ。前トピックまで戻さない。"""
    sents = [
        {
            "sentence": "前の話題です。",
            "start_time": 0.0,
            "end_time": 10.0,
            "start_char": 0,
            "end_char": 8,
        },
        {
            "sentence": "次の話題のフックです。",
            "start_time": 20.0,
            "end_time": 30.0,
            "start_char": 8,
            "end_char": 20,
        },
    ]
    clip = {
        "start_time": 15.0,
        "end_time": 28.0,
        "start_char": 8,
        "end_char": 18,
    }
    snapped = snap_clip_to_sentences(clip, sents)
    assert snapped["start_time"] == 20.0
    assert snapped["end_time"] == 30.0
    assert snapped["start_char"] == 8
    assert snapped["end_char"] == 20


def test_snap_trims_when_sentence_expansion_exceeds_max():
    """文境界スナップで最大尺を超えたら、先頭を残して縮める。"""
    sents = [
        {
            "sentence": "フック。",
            "start_time": 0.0,
            "end_time": 8.0,
            "start_char": 0,
            "end_char": 4,
        },
        {
            "sentence": "本論です。",
            "start_time": 8.0,
            "end_time": 50.0,
            "start_char": 4,
            "end_char": 9,
        },
        {
            "sentence": "補足です。",
            "start_time": 50.0,
            "end_time": 70.0,
            "start_char": 9,
            "end_char": 14,
        },
    ]
    # 2.0-58.0 (56秒) をスナップすると 0-70 (70秒) になり max=60 を超える
    clip = {
        "start_time": 2.0,
        "end_time": 58.0,
        "start_char": 1,
        "end_char": 12,
    }
    snapped = snap_clip_to_sentences(
        clip, sents, min_clip_duration=10, max_clip_duration=60
    )
    assert snapped["start_time"] == 0.0
    assert snapped["end_time"] == 50.0
    assert 10 <= snapped["end_time"] - snapped["start_time"] <= 60
    assert snapped["start_char"] == 0
    assert snapped["end_char"] == 9


def test_rank_keeps_clip_after_snap_would_have_exceeded_max():
    """スナップ後に尺オーバーした候補を捨てず、縮めて残す。"""
    sents = [
        {
            "sentence": "なぜPythonなのか。",
            "start_time": 0.0,
            "end_time": 10.0,
            "start_char": 0,
            "end_char": 12,
        },
        {
            "sentence": "文法が簡単だからです。",
            "start_time": 10.0,
            "end_time": 55.0,
            "start_char": 12,
            "end_char": 24,
        },
        {
            "sentence": "補足の説明です。",
            "start_time": 55.0,
            "end_time": 72.0,
            "start_char": 24,
            "end_char": 32,
        },
    ]
    text = "なぜPythonなのか。文法が簡単だからです。補足の説明です。"
    raw = {
        "start_time": 3.0,
        "end_time": 58.0,
        "start_char": 2,
        "end_char": 26,
    }
    snapped = snap_clip_to_sentences(
        raw, sents, min_clip_duration=15, max_clip_duration=60
    )
    kept = rank_and_suppress([snapped], text, 15, 60)
    assert len(kept) == 1
    assert kept[0]["end_time"] - kept[0]["start_time"] <= 60


def test_rank_and_suppress_skips_none_char_indices():
    text = "テストです。"
    clips = [
        {
            "start_time": 0.0,
            "end_time": 20.0,
            "start_char": None,
            "end_char": None,
        },
        {
            "start_time": 0.0,
            "end_time": 20.0,
            "start_char": 0,
            "end_char": len(text),
        },
    ]
    kept = rank_and_suppress(clips, text, 10, 60)
    assert len(kept) == 1
    assert kept[0]["start_char"] == 0


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


def test_llm_shorts_prompt_mentions_hooks():
    prompt = LlmClipFinder._build_prompt(
        "プレビュー",
        [{"index": 0, "start_time": 0, "end_time": 5, "sentence": "こんにちは。"}],
        10,
        60,
        for_shorts=True,
    )
    assert "YouTubeショート" in prompt
    assert "フック" in prompt
    longform = LlmClipFinder._build_prompt(
        "プレビュー",
        [{"index": 0, "start_time": 0, "end_time": 5, "sentence": "こんにちは。"}],
        10,
        60,
        for_shorts=False,
    )
    assert "トピック境界" in longform
