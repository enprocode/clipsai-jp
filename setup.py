from setuptools import find_packages, setup  # type: ignore

setup(
    name="clipsai",
    py_modules=["clipsai"],
    version="1.0.0",
    description=(
        "Clips AIは、長い動画を自動的にクリップに変換するオープンソースのPythonライブラリです"
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Benjamin Smidt, Johann Ramirez, Armel Talla",
    author_email="support@clipsai.com",
    url="https://clipsai.com/",
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        # コア依存関係（最小限）
        "numpy>=1.24.0",  # facenet-pytorch制約を削除、最新版使用可能
        "torch>=2.2.0",  # facenet-pytorch制約を削除、最新版使用可能
        
        # 音声/動画処理
        "av>=11.0.0,<17.0.0",
        "opencv-python>=4.5.0,<5.0.0",
        "scenedetect>=0.6.5,<0.7.0",
        
        # 機械学習（必須）
        "sentence-transformers>=3.0.0,<6.0.0",
        "scikit-learn>=1.3.0,<2.0.0",
        
        # 話者分離
        "pyannote.audio>=3.3.0,<5.0.0",
        "pyannote.core>=5.0.0,<7.0.0",
        
        # 顔検出・ランドマーク
        "mediapipe>=0.10.20,<0.11.0",
        
        # 自然言語処理
        "nltk>=3.8.0,<4.0.0",
        
        # ユーティリティ
        "psutil>=5.9.0,<8.0.0",
        "python-magic>=0.4.20,<0.5.0",
        "scipy>=1.9.0,<2.0.0",
    ],
    zip_safe=False,
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
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
            "pytest>=7.0.0,<9.0.0",
            "pandas>=2.0.0,<3.0.0",  # テスト用
            "matplotlib>=3.8.0,<4.0.0",  # 開発用
            "twine",
        ],
    },
)
