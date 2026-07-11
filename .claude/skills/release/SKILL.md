---
name: release
description: clipsai-jp の新バージョンを PyPI に公開する手順とチェックリスト。リリース、バージョンアップ、PyPI公開を頼まれたときに使用。
---

# PyPI リリース手順

## ブランチ運用

バージョンブランチ（例: `v1.0.5`）を作成 → 変更をコミット → PR → main へマージ、が既存の運用。

## チェックリスト（公開前に全て確認）

1. [ ] リポジトリ直下の `VERSION` ファイルを更新（**同一バージョンの再アップロードは不可**。setup.py・CI・`clipsai_jp.__version__` はすべてこのファイルから読む）
2. [ ] ルート直下の `CHANGELOG.md` に変更内容を追記
3. [ ] 依存関係の変更が `setup.py` と `requirements.txt` の**両方**に反映されている
4. [ ] 全テストがパス: `MECABRC=.venv/etc/mecabrc .venv/bin/python -m pytest tests/`
5. [ ] README.md が最新（PyPI プロジェクトページに表示される）

## ビルドと公開

```bash
rm -rf dist/                       # 再ビルド前に必ず削除
.venv/bin/pip install build twine
.venv/bin/python -m build

# 1. まず TestPyPI で動作確認
.venv/bin/twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ clipsai-jp

# 2. 問題なければ本番へ
.venv/bin/twine upload dist/*
```

GitHub Actions（`.github/workflows/python-publish.yml` / `python-publish-testpypi.yml`）による公開フローもある。認証は `~/.pypirc` の API トークン。

## 公開後

- git タグ付与とバージョンブランチの main へのマージを確認
  - 本番公開は GitHub Release の作成で自動発火する（Release タグと `VERSION` の一致が CI で検証される。タグは `v1.0.5` / `1.0.5` どちらの形式も可）
- `pip install clipsai-jp==<新バージョン>` で本番インストール確認
