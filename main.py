#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from openai import OpenAI


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
        description="ディレクトリ内の .ogg を一括文字起こしして TSV 出力"
    )
    parser.add_argument(
        "input_dir", help="OGG ファイルが格納されたディレクトリ"
    )
    parser.add_argument("output_tsv", help="出力 TSV ファイル名")
    parser.add_argument(
        "--model", default="whisper-1", help="Whisper モデル名 (例: whisper-1)"
    )
    args = parser.parse_args()

    # OpenAI クライアント初期化
    client = OpenAI()

    ogg_files = sorted(Path(args.input_dir).glob("*.ogg"))
    if not ogg_files:
        print(f"*.ogg ファイルが見つかりません: {args.input_dir}")
        return

    with open(args.output_tsv, "w", encoding="utf-8") as fo:
        fo.write("filename\ttranscription\n")
        for ogg in ogg_files:
            print(f"Transcribing {ogg.name} ...")
            text = transcribe_file(client, ogg, model=args.model)
            # 改行をスペースに置換
            text = text.replace("\n", " ").strip()
            fo.write(f"{ogg.name}\t{text}\n")

    print(f"完了: {args.output_tsv}")


if __name__ == "__main__":
    main()
