#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from openai import OpenAI


whitelist = [
    line
    for line in """

    """.strip().splitlines()
    if line.strip()
]


def is_in_list(x):
    """
    ファイル名がnew_listに含まれているかチェックする関数
    """
    return not whitelist or any(x.name in item for item in whitelist)


def transcribe_file(client, audio_path: Path, model: str = "whisper-1") -> str:
    """
    Whisper API にファイルを送信し、プレーンテキストで結果を返す。
    """
    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=model, file=f, response_format="text"
        )
    return resp  # 既に文字列


def main():
    parser = argparse.ArgumentParser(
        description="ディレクトリ内の音声ファイルを一括文字起こしして TSV 出力"
    )
    parser.add_argument(
        "input_dir", help="音声ファイルが格納されたディレクトリ"
    )
    parser.add_argument("output_tsv", help="出力 TSV ファイル名")
    parser.add_argument(
        "--model", default="whisper-1", help="Whisper モデル名 (例: whisper-1)"
    )
    args = parser.parse_args()

    # OpenAI クライアント初期化
    client = OpenAI()

    audio_files = sorted(
        list(Path(args.input_dir).glob("*.ogg"))
        + list(Path(args.input_dir).glob("*.wav"))
        + list(Path(args.input_dir).glob("*.mp3"))
        + list(Path(args.input_dir).glob("*.aac"))
    )
    if not audio_files:
        print(f"音声ファイルが見つかりません: {args.input_dir}")
        return

    with open(args.output_tsv, "w", encoding="utf-8") as fo:
        fo.write("filename\ttranscription\n")
        for audio_file in filter(is_in_list, audio_files):

            print(f"Transcribing {audio_file.name} ...")
            text = transcribe_file(client, audio_file, model=args.model)
            # 改行をスペースに置換
            text = text.replace("\n", " ").strip()
            fo.write(f"{audio_file.name}\t{text}\n")

    print(f"完了: {args.output_tsv}")


if __name__ == "__main__":
    main()
