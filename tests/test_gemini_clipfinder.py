"""
GeminiClipFinder のチャンク分割ロジックのテスト

実際のGemini APIは呼ばず、client をフェイクに差し替えて
「長尺（多数の文）でも全チャンクに問い合わせ、結果を統合・重複除去する」
ことを検証する。
"""

import json

from clipsai_jp.clip import gemini_clipfinder as gcf
from clipsai_jp.clip.gemini_clipfinder import GeminiClipFinder


class _FakeResponse:
    def __init__(self, text):
        self.text = text


class _FakeModels:
    def __init__(self, recorder):
        self._recorder = recorder

    def generate_content(self, model, contents):
        # プロンプトを記録し、含まれる文インデックスに応じた境界を返す
        self._recorder.append(contents)
        # プロンプト内の sentences_summary を解析して、そのチャンクの
        # 先頭 index を使った一意な境界を返す
        first_index = None
        for line in contents.splitlines():
            line = line.strip().rstrip(",")
            if line.startswith('"index"'):
                first_index = int(line.split(":")[1].strip())
                break
        start = float(first_index or 0)
        return _FakeResponse(
            json.dumps(
                [
                    {
                        "start_time": start,
                        "end_time": start + 30,
                        "topic": "t",
                        "reason": "r",
                        "sentence_indices": [first_index, first_index],
                    }
                ]
            )
        )


class _FakeClient:
    def __init__(self, recorder):
        self.models = _FakeModels(recorder)


def _make_finder(recorder):
    # __init__ を通さずにインスタンスを作り、必要な属性だけ設定する
    finder = GeminiClipFinder.__new__(GeminiClipFinder)
    finder.client = _FakeClient(recorder)
    finder.model_name = "fake-model"
    return finder


def _sentences(n):
    return [
        {"start_time": float(i), "end_time": float(i) + 1.0, "sentence": f"文{i}。"}
        for i in range(n)
    ]


def test_empty_sentences_returns_empty():
    finder = _make_finder([])
    assert finder.suggest_clip_boundaries("", []) == []


def test_single_chunk_calls_once():
    recorder = []
    finder = _make_finder(recorder)
    result = finder.suggest_clip_boundaries("", _sentences(10))
    assert len(recorder) == 1  # 1回だけ問い合わせ
    assert len(result) == 1


def test_long_input_is_chunked_into_multiple_requests():
    """SENTENCES_PER_CHUNK を超える文数では複数回問い合わせる"""
    recorder = []
    finder = _make_finder(recorder)
    n = gcf.SENTENCES_PER_CHUNK * 3  # 3チャンク相当
    result = finder.suggest_clip_boundaries("", _sentences(n))

    # 少なくとも3回は問い合わせている（後半の文もカバーされる）
    assert len(recorder) >= 3
    # 各チャンクが別の境界を返すので統合結果も複数
    assert len(result) >= 3


def test_indices_are_global_across_chunks():
    """2チャンク目以降の index が index_offset で全体一貫になっている"""
    recorder = []
    finder = _make_finder(recorder)
    n = gcf.SENTENCES_PER_CHUNK * 2
    finder.suggest_clip_boundaries("", _sentences(n))

    # 2回目の問い合わせプロンプトには先頭が0ではないindexが含まれる
    assert '"index": 0' in recorder[0]
    second_prompt = recorder[1]
    # 2チャンク目の先頭 index は step (=SENTENCES_PER_CHUNK - CHUNK_OVERLAP)
    step = gcf.SENTENCES_PER_CHUNK - gcf.CHUNK_OVERLAP
    assert f'"index": {step}' in second_prompt


def test_dedupe_removes_near_duplicate_boundaries():
    boundaries = [
        {"start_time": 10.0, "end_time": 40.0},
        {"start_time": 10.5, "end_time": 40.5},  # 2秒以内 → 重複
        {"start_time": 100.0, "end_time": 130.0},
    ]
    unique = GeminiClipFinder._dedupe_boundaries(boundaries)
    assert len(unique) == 2
    # start_time 昇順
    assert unique[0]["start_time"] == 10.0
    assert unique[1]["start_time"] == 100.0
