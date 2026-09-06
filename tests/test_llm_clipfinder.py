"""
LlmClipFinder のチャンク分割・プロバイダ別リクエスト組み立てのテスト。

実際の LLM API は呼ばず、``_complete`` を差し替えて検証する。
"""

import json
from unittest.mock import patch

import pytest

from clipsai_jp.clip import llm_clipfinder as lcf
from clipsai_jp.clip.llm_clipfinder import LlmClipFinder


def _make_finder(recorder, provider="openai"):
    finder = LlmClipFinder.__new__(LlmClipFinder)
    finder.provider = provider
    finder.model_name = "fake-model"
    finder.base_url = "https://example.invalid/v1"
    finder.api_key = "fake-key"
    finder.timeout = 5

    def _complete(prompt):
        recorder.append(prompt)
        first_index = None
        for line in prompt.splitlines():
            line = line.strip().rstrip(",")
            if line.startswith('"index"'):
                first_index = int(line.split(":")[1].strip())
                break
        start = float(first_index or 0)
        return json.dumps(
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

    finder._complete = _complete
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
    assert len(recorder) == 1
    assert len(result) == 1


def test_long_input_is_chunked_into_multiple_requests():
    """SENTENCES_PER_CHUNK を超える文数では複数回問い合わせる"""
    recorder = []
    finder = _make_finder(recorder)
    n = lcf.SENTENCES_PER_CHUNK * 3
    result = finder.suggest_clip_boundaries("", _sentences(n))

    assert len(recorder) >= 3
    assert len(result) >= 3


def test_indices_are_global_across_chunks():
    """2チャンク目以降の index が index_offset で全体一貫になっている"""
    recorder = []
    finder = _make_finder(recorder)
    n = lcf.SENTENCES_PER_CHUNK * 2
    finder.suggest_clip_boundaries("", _sentences(n))

    assert '"index": 0' in recorder[0]
    second_prompt = recorder[1]
    step = lcf.SENTENCES_PER_CHUNK - lcf.CHUNK_OVERLAP
    assert f'"index": {step}' in second_prompt


def test_dedupe_removes_near_duplicate_boundaries():
    boundaries = [
        {"start_time": 10.0, "end_time": 40.0},
        {"start_time": 10.5, "end_time": 40.5},
        {"start_time": 100.0, "end_time": 130.0},
    ]
    unique = LlmClipFinder._dedupe_boundaries(boundaries)
    assert len(unique) == 2
    assert unique[0]["start_time"] == 10.0
    assert unique[1]["start_time"] == 100.0


def test_unsupported_provider_raises():
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        LlmClipFinder(provider="unknown", api_key="k")


def test_openai_compatible_requires_base_url():
    with pytest.raises(ValueError, match="llm_base_url"):
        LlmClipFinder(
            provider="openai_compatible",
            api_key="k",
            model="llama3",
        )


def test_openai_compatible_allows_missing_api_key():
    finder = LlmClipFinder(
        provider="openai-compatible",
        model="llama3",
        base_url="http://localhost:11434/v1",
    )
    assert finder.provider == "openai_compatible"
    assert finder.api_key is None


def test_default_models_are_current():
    finder_openai = LlmClipFinder(provider="openai", api_key="k")
    finder_anthropic = LlmClipFinder(provider="anthropic", api_key="k")
    finder_gemini = LlmClipFinder(provider="gemini", api_key="k")
    assert finder_openai.model_name == "gpt-5.6-terra"
    assert finder_anthropic.model_name == "claude-sonnet-5"
    assert finder_gemini.model_name == "gemini-3.8-flash"


def test_openai_request_uses_chat_completions():
    finder = LlmClipFinder(provider="openai", api_key="sk-test", model="gpt-5.6-terra")
    url, headers, payload = finder._build_request("hello")
    assert url.endswith("/chat/completions")
    assert headers["Authorization"] == "Bearer sk-test"
    assert payload["model"] == "gpt-5.6-terra"
    assert payload["messages"][0]["content"] == "hello"


def test_anthropic_request_uses_messages_api():
    finder = LlmClipFinder(
        provider="anthropic", api_key="ant-test", model="claude-sonnet-5"
    )
    url, headers, payload = finder._build_request("hello")
    assert url.endswith("/v1/messages")
    assert headers["x-api-key"] == "ant-test"
    assert payload["model"] == "claude-sonnet-5"
    assert "temperature" not in payload


def test_gemini_request_uses_generate_content():
    finder = LlmClipFinder(
        provider="gemini", api_key="gem-test", model="gemini-3.8-flash"
    )
    url, headers, payload = finder._build_request("hello")
    assert "models/gemini-3.8-flash:generateContent" in url
    assert headers["x-goog-api-key"] == "gem-test"
    assert payload["contents"][0]["parts"][0]["text"] == "hello"
    assert "temperature" not in payload["generationConfig"]


def test_extract_text_openai():
    finder = LlmClipFinder(provider="openai", api_key="k")
    text = finder._extract_text(
        {"choices": [{"message": {"content": '[{"start_time": 1}]'}}]}
    )
    assert text == '[{"start_time": 1}]'


def test_extract_text_anthropic():
    finder = LlmClipFinder(provider="anthropic", api_key="k")
    text = finder._extract_text({"content": [{"type": "text", "text": "ok"}]})
    assert text == "ok"


def test_extract_text_gemini():
    finder = LlmClipFinder(provider="gemini", api_key="k")
    text = finder._extract_text(
        {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
    )
    assert text == "ok"


def test_shorts_prompt_mentions_hooks():
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


def test_clipfinder_use_llm_initializes_finder():
    from clipsai_jp.clip.clipfinder import ClipFinder

    created = {}

    class _FakeLlm:
        def __init__(self, **kwargs):
            created.update(kwargs)
            self.provider = kwargs["provider"]
            self.model_name = kwargs.get("model") or "fake"

    with patch("clipsai_jp.clip.clipfinder.LlmClipFinder", _FakeLlm):
        finder = ClipFinder(
            device="cpu",
            use_llm=True,
            llm_provider="openai",
            llm_api_key="sk-test",
            llm_model="gpt-5.6-terra",
            llm_priority=0.7,
        )

    assert finder._use_llm is True
    assert created["provider"] == "openai"
    assert created["api_key"] == "sk-test"
    assert created["model"] == "gpt-5.6-terra"
    assert finder._llm_priority == 0.7


def test_clipfinder_use_gemini_maps_to_gemini_provider():
    from clipsai_jp.clip.clipfinder import ClipFinder

    created = {}

    class _FakeLlm:
        def __init__(self, **kwargs):
            created.update(kwargs)
            self.provider = kwargs["provider"]
            self.model_name = kwargs.get("model") or "fake"

    with patch("clipsai_jp.clip.clipfinder.LlmClipFinder", _FakeLlm):
        with pytest.warns(DeprecationWarning, match="use_gemini"):
            finder = ClipFinder(
                device="cpu",
                use_gemini=True,
                gemini_api_key="gem-test",
                gemini_model="gemini-3.8-flash",
            )

    assert finder._use_llm is True
    assert created["provider"] == "gemini"
    assert created["api_key"] == "gem-test"
    assert created["model"] == "gemini-3.8-flash"


def test_clipfinder_legacy_positional_args_still_map_to_use_gemini():
    """embedding_model の次の位置引数は use_gemini のまま（後方互換）。"""
    from clipsai_jp.clip.clipfinder import ClipFinder

    created = {}

    class _FakeLlm:
        def __init__(self, **kwargs):
            created.update(kwargs)
            self.provider = kwargs["provider"]
            self.model_name = kwargs.get("model") or "fake"

    with patch("clipsai_jp.clip.clipfinder.LlmClipFinder", _FakeLlm):
        with pytest.warns(DeprecationWarning, match="use_gemini"):
            finder = ClipFinder(
                "cpu",
                15,
                900,
                "high",
                "max",
                3,
                "mean",
                "japanese",
                True,
                "gem-test",
            )

    assert finder._use_llm is True
    assert created["provider"] == "gemini"
    assert created["api_key"] == "gem-test"


def test_clipfinder_new_llm_args_are_keyword_only():
    import inspect

    from clipsai_jp.clip.clipfinder import ClipFinder

    params = inspect.signature(ClipFinder.__init__).parameters
    names = list(params)
    assert names.index("use_gemini") < names.index("use_llm")
    assert names.index("clip_style") < names.index("use_llm")
    assert names.index("max_clips") < names.index("use_llm")
    assert params["use_llm"].kind is inspect.Parameter.KEYWORD_ONLY
    assert params["llm_priority"].kind is inspect.Parameter.KEYWORD_ONLY


def test_llm_priority_zero_skips_llm_init():
    from clipsai_jp.clip.clipfinder import ClipFinder

    class _FakeLlm:
        def __init__(self, **kwargs):
            raise AssertionError("LlmClipFinder should not be constructed")

        def suggest_clip_boundaries(self, *a, **k):
            raise AssertionError("LLM API should not be called")

    with patch("clipsai_jp.clip.clipfinder.LlmClipFinder", _FakeLlm):
        finder = ClipFinder(
            device="cpu",
            use_llm=True,
            llm_api_key="sk-test",
            llm_priority=0.0,
        )

    assert finder._use_llm is False
    assert finder._llm_finder is None
    assert finder._llm_priority == 0.0


def test_gemini_clipfinder_wrapper_is_llm_subclass():
    from clipsai_jp.clip.gemini_clipfinder import GeminiClipFinder

    assert issubclass(GeminiClipFinder, LlmClipFinder)
    with pytest.warns(DeprecationWarning, match="GeminiClipFinder is deprecated"):
        finder = GeminiClipFinder(api_key="gem-test")
    assert finder.provider == "gemini"
