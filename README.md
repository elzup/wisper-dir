# wisper-dir

> Batch Transcriber (using Whisper)

This is a Python script that batch transcribes OGG audio files in a specified directory and outputs the results to a TSV file. It utilizes OpenAI's Whisper model.

## Requirements

- Python 3.x
- Whisper (openai-whisper)
- OpenAI API Key

```
export OPENAI_API_KEY=""
```

## Usage

```bash
python main.py <input_directory> <output_tsv_file> [options]
```

support file types `.ogg .wav .mp3 .aac`

**Arguments:**

- `input_directory`: Path to the directory containing the meida files to be transcribed (required)
- `output_tsv_file`: Path to the TSV file to output the transcription results (required)

**Options:**

- `--model <model_name>`: Whisper model name to use (default: `small`)
  - Available models: `tiny`, `base`, `small`, `medium`, `large`
- `--lang <language_code>`: Language code for the language to be transcribed (default: `ja`)
  - Example: `ja` (Japanese), `en` (English)

**Example Usage:**

```bash
# Transcribe OGG files in the data/ogg directory using the medium model for Japanese and output to result.tsv
python main.py data/ogg result.tsv --model medium --lang ja
```

## TSV Output Format

The output TSV file will be in the following format (tab-separated).

```
filename	transcription
audio1.ogg	This is the first audio file.
audio2.ogg	This is the transcription result of the second audio file.
...
```
