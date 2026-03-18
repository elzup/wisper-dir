# wisper-dir

> Batch Transcriber (using Whisper)

Batch transcribe audio files in a directory and output results to a TSV file using OpenAI's Whisper API.

## Install

```bash
pip install wisper-dir
# or
pipx install wisper-dir
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
- `--setup`: Save API key to `~/.config/wisper-dir/config.json`

**Example:**

```bash
wisper-dir data/ogg result.tsv
```

## TSV Output Format

```
filename	transcription
audio1.ogg	This is the first audio file.
audio2.ogg	This is the transcription result of the second audio file.
...
```
