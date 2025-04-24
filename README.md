#n OGG Batch Transcriber (using Whisper)

指定されたディレクトリ内の OGG 音声ファイルを一括で文字起こしし、結果を TSV ファイルに出力する Python スクリプトです。OpenAI の Whisper モデルを利用しています。

## 必要なもの

- Python 3.x
- Whisper (openai-whisper)

## インストール

1.  **Whisper のインストール:**
    ```bash
    pip install -U openai-whisper
    ```
    (環境によっては追加の依存関係が必要になる場合があります。詳細は [Whisper GitHub リポジトリ](https://github.com/openai/whisper#setup) を参照してください。)

## 使い方

コマンドラインから `main.py` を実行します。

```bash
python main.py <input_directory> <output_tsv_file> [options]
```

**引数:**

- `input_directory`: 文字起こし対象の OGG ファイルが含まれるディレクトリのパス (必須)
- `output_tsv_file`: 文字起こし結果を出力する TSV ファイルのパス (必須)

**オプション:**

- `--model <model_name>`: 使用する Whisper モデル名 (デフォルト: `small`)
  - 利用可能なモデル: `tiny`, `base`, `small`, `medium`, `large`
- `--lang <language_code>`: 文字起こしする言語のコード (デフォルト: `ja`)
  - 例: `ja` (日本語), `en` (英語)

**実行例:**

```bash
# data/ogg ディレクトリ内の OGG ファイルを medium モデルで日本語文字起こしし、result.tsv に出力
python main.py data/ogg result.tsv --model medium --lang ja
```

## TSV 出力形式

出力される TSV ファイルは以下の形式です (タブ区切り)。

```
filename	transcription
audio1.ogg	これは最初の音声ファイルです。
audio2.ogg	これは二番目の音声ファイルの文字起こし結果です。
...
```

## Contributing

貢献に関するガイドラインです。(必要に応じて追記)

## License

このプロジェクトのライセンス情報です。(必要に応じて追記)
