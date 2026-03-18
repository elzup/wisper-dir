#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
from pathlib import Path
from openai import OpenAI


CONFIG_DIR = Path.home() / ".config" / "wisper-dir"
CONFIG_FILE = CONFIG_DIR / "config.json"


whitelist = [
    line
    for line in """

    """.strip().splitlines()
    if line.strip()
]


def load_api_key() -> str | None:
    """config ファイルから API キーを読み込む。"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
        return config.get("openai_api_key")
    return None


def setup_config():
    """対話的に API キーを設定して config ファイルに保存する。"""
    print(f"wisper-dir セットアップ (設定先: {CONFIG_FILE})")
    api_key = input("OpenAI API Key: ").strip()
    if not api_key:
        print("API キーが空です。中止します。")
        sys.exit(1)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
    config["openai_api_key"] = api_key
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    CONFIG_FILE.chmod(0o600)
    print(f"保存しました: {CONFIG_FILE}")


def get_openai_client() -> OpenAI:
    """環境変数 → config ファイルの順で API キーを解決して OpenAI クライアントを返す。"""
    api_key = os.environ.get("OPENAI_API_KEY") or load_api_key()
    if not api_key:
        print(
            "OPENAI_API_KEY が見つかりません。\n"
            "  環境変数に設定するか、`--setup` で初期設定してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    return OpenAI(api_key=api_key)


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
        "input_dir", nargs="?", help="音声ファイルが格納されたディレクトリ"
    )
    parser.add_argument("output_tsv", nargs="?", help="出力 TSV ファイル名")
    parser.add_argument(
        "--model", default="whisper-1", help="Whisper モデル名 (例: whisper-1)"
    )
    parser.add_argument(
        "--setup", action="store_true", help="API キーを ~/.config/wisper-dir に設定"
    )
    args = parser.parse_args()

    if args.setup:
        setup_config()
        return

    if not args.input_dir or not args.output_tsv:
        parser.error("input_dir と output_tsv は必須です")

    client = get_openai_client()

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
