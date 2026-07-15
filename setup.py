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
        "av>=11.0.0,<17.0.0",
        "opencv-python>=4.5.0,<5.0.0",
        "scenedetect>=0.6.5,<0.8.0",
        
        # 機械学習（必須）
        "sentence-transformers>=3.0.0,<6.0.0",
        "scikit-learn>=1.3.0,<2.0.0",
        
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
        "nltk>=3.8.0,<4.0.0",
        
        # ユーティリティ
        "psutil>=5.9.0,<8.0.0",
        "python-magic>=0.4.20,<0.5.0",
        "scipy>=1.9.0,<2.0.0",
        
        # Gemini API（クリップ検出精度向上用）
        "google-genai>=1.0.0",
    ],
    zip_safe=False,
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
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
            "pynvml>=11.0.0,<14.0.0",
        ],
        # 開発・テスト用
        "dev": [
            "black",
            "black[jupyter]",
            "build",
            "flake8",
            "ipykernel",
            "pytest>=7.0.0,<10.0.0",
            "pandas>=2.0.0,<3.0.0",  # テスト用
            "matplotlib>=3.8.0,<4.0.0",  # 開発用
            "twine",
        ],
    },
)
