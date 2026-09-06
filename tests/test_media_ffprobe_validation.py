"""ffprobe 引数の注入防止テスト。"""

import pytest

from clipsai_jp.filesys.exceptions import FileSystemObjectError
from clipsai_jp.media.exceptions import MediaFileError
from clipsai_jp.media.media_file import MediaFile


def test_get_format_info_rejects_injection_payload():
    media_file = MediaFile("/tmp/nonexistent.mp4")
    with pytest.raises(MediaFileError, match="format_field"):
        media_file.get_format_info("duration;malicious")


def test_get_stream_info_rejects_injection_payload():
    media_file = MediaFile("/tmp/nonexistent.mp4")
    with pytest.raises(MediaFileError, match="stream_field"):
        media_file.get_stream_info("v:0", "width,format=evil")


def test_get_stream_info_rejects_invalid_stream_selector():
    media_file = MediaFile("/tmp/nonexistent.mp4")
    with pytest.raises(MediaFileError, match="stream"):
        media_file.get_stream_info("v:0;id", "width")


@pytest.mark.parametrize("stream", ["v", "a", "v:0", "a:0"])
def test_get_stream_info_accepts_valid_selectors_before_missing_file(stream):
    media_file = MediaFile("/tmp/nonexistent.mp4")
    with pytest.raises(FileSystemObjectError):
        media_file.get_stream_info(stream, "width")
