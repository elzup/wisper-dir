# wisper-dir

> Batch Transcriber (using Whisper)

Batch transcribe audio files in a directory and output results to a TSV file using OpenAI's Whisper API or `mlx-whisper`.

## Install

```bash
pip install wisper-dir
# or
pipx install wisper-dir
```

`mlx-whisper` backend を使う場合:

```bash
pip install "wisper-dir[mlx]"
```

カタカナ読み変換を使う場合:

```bash
pip install "wisper-dir[kana]"
```

## Setup

```bash
# 初回セットアップ: API キーを ~/.config/wisper-dir/config.json に保存
wisper-dir --setup
```

環境変数 `OPENAI_API_KEY` が設定されている場合はそちらが優先されます。

## Usage

```bash
wisper-dir <input_directory> <output_tsv_file> [options]
```

Supported file types: `.ogg .wav .mp3 .aac`

**Arguments:**

- `input_directory`: Path to the directory containing the media files to be transcribed (required)
- `output_tsv_file`: Path to the TSV file to output the transcription results (required)

**Options:**

- `--model <model_name>`: Whisper model name to use (default: `whisper-1`)
- `--backend <openai|mlx>`: transcription backend (default: `openai`)
- `--language <lang|auto>`: language code (default: `ja`)
- `--prompt <text>`: initial prompt passed to the transcription backend
- `--katakana-reading`: convert the transcript to katakana reading after transcription
- `--benchmark`: output per-file elapsed time as a benchmark TSV
- `--benchmark-output <path>`: path for benchmark TSV (default: `<output_tsv>.bench.tsv`)
- `--setup`: Save API key to `~/.config/wisper-dir/config.json`

**Example:**

```bash
wisper-dir data/ogg result.tsv
```

OpenAI backend と MLX backend の比較:

```bash
wisper-dir data/ogg openai.tsv --backend openai --model whisper-1 --benchmark
wisper-dir data/ogg mlx.tsv --backend mlx --model mlx-community/whisper-large-v3-turbo --benchmark
```

漢字を避けたカタカナ読み出力:

```bash
wisper-dir data/ogg reading.tsv --katakana-reading
```

## TSV Output Format

```
filename	transcription
audio1.ogg	This is the first audio file.
audio2.ogg	This is the transcription result of the second audio file.
...
```

## Notes

- `--katakana-reading` は ASR 後に `pykakasi` で読みへ変換します。完全な固有名詞読みや文脈依存の語は誤る場合があります。
- `--prompt` は OpenAI / MLX の両 backend に渡します。日本語表記の傾向を多少誘導できますが、「絶対に漢字にしない」はモデル単体では保証できません。
