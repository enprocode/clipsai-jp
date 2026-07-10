"""
日本語文分割（japanese_sentence_splitter）のテスト

MeCab本体はCI環境にないため、MeCabを必要としない
モジュールレベル関数 split_japanese_sentences をテストする。
"""

import pytest

from clipsai_jp.transcribe.japanese_sentence_splitter import (
    MAX_SENTENCE_LENGTH,
    split_japanese_sentences,
)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", []),
        ("   ", []),
        ("こんにちは。今日は良い天気です。", ["こんにちは。", "今日は良い天気です。"]),
        ("え！？そうなんですか？", ["え！", "？", "そうなんですか？"]),
        ("改行\nで分割\nされます", ["改行\n", "で分割\n", "されます"]),
        ("句点なしの短いテキスト", ["句点なしの短いテキスト"]),
        ("。", ["。"]),
        # 句点後の空白は次の文の先頭に保持される（部分文字列性の維持）
        ("こんにちは。 今日は良い天気です。", ["こんにちは。", " 今日は良い天気です。"]),
    ],
)
def test_split_basic(text, expected):
    assert split_japanese_sentences(text) == expected


def test_split_results_are_substrings():
    """全分割結果が元テキストの部分文字列であること（タイムスタンプマッピングの前提）"""
    text = "文A。 文B！\n文C？句点なしで終わる文"
    for sentence in split_japanese_sentences(text):
        assert sentence in text


def test_fallback_splits_punctuation_less_transcript_on_spaces():
    """句読点のない文字起こし（Whisperの日本語出力で発生）はスペースで再分割される"""
    # Whisperのセグメント出力を模擬: 句読点なし、セグメント間はスペース
    segments = [f"セグメント{i}の発話内容がここに入ります" for i in range(30)]
    text = " ".join(segments)
    assert len(text) > MAX_SENTENCE_LENGTH

    result = split_japanese_sentences(text)

    # 1文にまとまらず、セグメント粒度に分割されること
    assert len(result) == 30
    # 部分文字列性の維持
    for sentence in result:
        assert sentence in text


def test_fallback_chunks_text_without_spaces():
    """スペースすらない極端に長いテキストは固定長で分割される"""
    text = "あ" * (MAX_SENTENCE_LENGTH * 3)
    result = split_japanese_sentences(text)

    assert len(result) == 3
    assert all(len(s) <= MAX_SENTENCE_LENGTH for s in result)
    assert "".join(result) == text


def test_short_sentences_not_affected_by_fallback():
    """通常の句読点付きテキストはフォールバックの影響を受けない"""
    text = "短い文。" * 100  # 個々の文は短いが全体は長い
    result = split_japanese_sentences(text)
    assert result == ["短い文。"] * 100


def test_long_sentence_with_punctuation_mixed():
    """句読点のある文と長すぎる文が混在する場合、長い文だけ再分割される"""
    long_part = " ".join(["長い発話パート"] * 40)
    text = f"普通の文。{long_part}"
    result = split_japanese_sentences(text)

    assert result[0] == "普通の文。"
    assert len(result) > 2  # 長い部分が複数に分割されている
    for sentence in result:
        assert sentence in text
