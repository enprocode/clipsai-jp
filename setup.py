import os

from setuptools import find_packages, setup  # type: ignore

# バージョンはVERSIONファイルで一元管理する（リリース時はVERSIONのみ更新）
_here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(_here, "VERSION"), encoding="utf-8") as _f:
    _version = _f.read().strip()

setup(
    name="clipsai-jp",
    version=_version,
    description=(
        "Clips AIは、長い動画を自動的にクリップに変換するオープンソースのPythonライブラリです（日本語専用版）"
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Enpro",
    author_email="support@enprocode.com",
    url="https://enprocode.com/",
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        # コア依存関係（最小限）
        # mediapipe が numpy<2 を要求するため 2.0 未満に制限
        "numpy>=1.24.0,<2.0.0",
        
        # 文字起こし（faster-whisperを使用）
        "faster-whisper>=1.0.0,<2.0.0",
        
        # torch は pyannote.audio の要件に合わせて設定
        # pyannote.audio 3.3.0+ は torch>=2.0.0 を要求
        # torchaudio 2.9.0以降ではAudioMetaDataが削除されているため、torchも2.9.0未満に制限
        "torch>=2.0.0,<2.9.0",
        # torchaudio は torch のバージョンと一致させる必要がある
        # torchaudio 2.9.0以降ではAudioMetaDataが削除されているため、2.8.0以下に制限
        "torchaudio>=2.0.0,<2.9.0",
        
        # 音声/動画処理
        # av 17.1.0 は CVE-2026-40962 対応のため FFmpeg 8.1.1 をバンドル
        # （17.x は Python >=3.10。18.x は Python >=3.11 のため 18 未満に制限）
        "av>=17.1.0,<18.0.0",
        # 4.12+ / 5.x は Python>=3.9 で numpy>=2 を要求し、mediapipe の numpy<2 と衝突
        "opencv-python>=4.11.0.86,<4.12.0",
        "scenedetect>=0.7.1,<0.8.0",

        # 機械学習（必須）
        "sentence-transformers>=6.0.1,<7.0.0",
        "scikit-learn>=1.7.2,<2.0.0",
        # sentence-transformers 6.x は transformers 5.x を要求する。
        # 4.x 系には RCE 等の未修正 CVE が残るため 5.16.1 以上に固定
        "transformers>=5.16.1,<6.0.0",
        # Pillow 12.3.0 で 2026 年の OOB / bomb 系 CVE が修正済み
        "pillow>=12.3.0",

        # 話者分離
        # pyannote.audio 4.x は torchcodec>=0.7 を要求し、torchcodec は torch 2.9以降
        # とペアになるため、本プロジェクトの torch<2.9 制約と衝突する（import不能になる）
        # → torchcodec不要の3.x系に制限
        "pyannote.audio>=3.3.0,<4.0.0",
        # pyannote.audio 3.x は pyannote.core<6.0 を要求するため 6.0 未満に制限
        "pyannote.core>=5.0.0,<6.0.0",
        
        # 顔検出・ランドマーク
        # MediaPipe 0.10.30以降ではレガシーsolutions APIが削除されているため、
        # 0.10.30未満に制限（0.10.21がsolutions APIを持つ最後のバージョン）
        "mediapipe>=0.10.20,<0.10.30",
        
        # 自然言語処理
        # 3.10.3 で pickle RCE / SSRF / path traversal 等を修正
        # （3.10.x は Python >=3.10。CVE-2026-81726 は 3.10.3 時点で未修正）
        "nltk>=3.10.3,<4.0.0",

        # ユーティリティ
        "psutil>=5.9.0,<8.0.0",
        "python-magic>=0.4.27,<0.5.0",
        "scipy>=1.9.0,<2.0.0",
        # huggingface-hub / nltk 経由の間接依存。既知 CVE の修正版に固定
        "urllib3>=2.7.0",
        "requests>=2.34.2",
        "jinja2>=3.1.6",
    ],
    zip_safe=False,
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://docs.clipsai.com/",
        "Homepage": "https://clipsai.com/",
        "Repository": "https://github.com/enprocode/clipsai-jp",
        "Issues": "https://github.com/enprocode/clipsai-jp/issues",
    },
    include_package_data=True,
    extras_require={
        # 日本語形態素解析（オプション、推奨）
        # MeCabがインストールされていない場合、自動的にNLTKにフォールバックします
        # mecabパッケージはMeCab本体も含まれており、Windowsでもpip installのみで使用可能
        # 公式サイト: https://pypi.org/project/mecab/
        "mecab": [
            "mecab>=0.996.0",
        ],
        # GPUメモリ監視（オプション）
        "gpu": [
            "pynvml>=13.0.1,<14.0.0",
        ],
        # 開発・テスト用
        "dev": [
            "black",
            "black[jupyter]",
            "build",
            "flake8",
            "ipykernel",
            "pytest>=9.1.1,<10.0.0",
            "pandas>=2.0.0,<3.0.0",  # テスト用
            "matplotlib>=3.8.0,<4.0.0",  # 開発用
            "twine",
        ],
    },
)
