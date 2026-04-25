import argparse
import json
import os
import sys
import time
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
            "  環境変数に設定するか、`wisper-dir --setup` で初期設定してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    return OpenAI(api_key=api_key)


def resolve_katakana_converter():
    """pykakasi を使うカタカナ変換関数を返す。"""
    try:
        from pykakasi import kakasi
    except ImportError:
        print(
            "カタカナ読み出力には `pykakasi` が必要です。\n"
            "  `pip install pykakasi` を実行してから再試行してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    converter = kakasi()

    def to_katakana(text: str) -> str:
        chunks = []
        for item in converter.convert(text):
            kana = item.get("kana") or item.get("orig") or ""
            chunks.append(kana)
        return "".join(chunks)

    return to_katakana


def is_in_list(x):
    """
    ファイル名がnew_listに含まれているかチェックする関数
    """
    return not whitelist or any(x.name in item for item in whitelist)


def transcribe_with_openai(
    client: OpenAI,
    audio_path: Path,
    model: str,
    language: str | None,
    prompt: str | None,
) -> str:
    """OpenAI Audio API で文字起こしする。"""
    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="text",
            language=language,
            prompt=prompt,
        )
    return resp  # 既に文字列


def transcribe_with_mlx(
    audio_path: Path,
    model: str,
    language: str | None,
    prompt: str | None,
) -> str:
    """mlx-whisper でローカル文字起こしする。"""
    try:
        import mlx_whisper
    except ImportError:
        print(
            "mlx backend には `mlx-whisper` が必要です。\n"
            "  `pip install mlx-whisper` を実行してから再試行してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    resp = mlx_whisper.transcribe(
        str(audio_path),
        path_or_hf_repo=model,
        language=language,
        initial_prompt=prompt,
    )
    return str(resp.get("text", "")).strip()


def transcribe_file(
    backend: str,
    audio_path: Path,
    model: str,
    language: str | None,
    prompt: str | None,
    client: OpenAI | None = None,
) -> str:
    """選択された backend で文字起こしする。"""
    if backend == "openai":
        if client is None:
            raise ValueError("openai backend には client が必要です")
        return transcribe_with_openai(client, audio_path, model, language, prompt)
    if backend == "mlx":
        return transcribe_with_mlx(audio_path, model, language, prompt)
    raise ValueError(f"Unsupported backend: {backend}")


def main():
    parser = argparse.ArgumentParser(
        prog="wisper-dir",
        description="ディレクトリ内の音声ファイルを一括文字起こしして TSV 出力",
    )
    parser.add_argument(
        "input_dir", nargs="?", help="音声ファイルが格納されたディレクトリ"
    )
    parser.add_argument("output_tsv", nargs="?", help="出力 TSV ファイル名")
    parser.add_argument(
        "--model", default="whisper-1", help="Whisper モデル名 (例: whisper-1)"
    )
    parser.add_argument(
        "--backend",
        choices=["openai", "mlx"],
        default="openai",
        help="文字起こし backend (default: openai)",
    )
    parser.add_argument(
        "--language",
        default="ja",
        help="音声言語コード。自動判定したい場合は `auto` を指定",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="文字起こし時に渡す初期プロンプト",
    )
    parser.add_argument(
        "--katakana-reading",
        action="store_true",
        help="文字起こし後に漢字をカタカナ読みに変換して出力",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="処理時間を計測してベンチマーク TSV も出力",
    )
    parser.add_argument(
        "--benchmark-output",
        default=None,
        help="ベンチマーク TSV の出力先。未指定時は `<output>.bench.tsv`",
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

    language = None if args.language == "auto" else args.language
    prompt = args.prompt
    if args.katakana_reading and not prompt:
        prompt = (
            "出力は漢字をなるべく避け、読みが分かる形を優先してください。"
            "固有名詞や外来語はカタカナ寄りで出力してください。"
        )

    client = get_openai_client() if args.backend == "openai" else None
    katakana_converter = (
        resolve_katakana_converter() if args.katakana_reading else None
    )

    audio_files = sorted(
        list(Path(args.input_dir).glob("*.ogg"))
        + list(Path(args.input_dir).glob("*.wav"))
        + list(Path(args.input_dir).glob("*.mp3"))
        + list(Path(args.input_dir).glob("*.aac"))
    )
    if not audio_files:
        print(f"音声ファイルが見つかりません: {args.input_dir}")
        return

    benchmark_output = (
        args.benchmark_output
        if args.benchmark_output
        else f"{args.output_tsv}.bench.tsv"
    )

    with open(args.output_tsv, "w", encoding="utf-8") as fo:
        fo.write("filename\ttranscription\n")
        bench = None
        if args.benchmark:
            bench = open(benchmark_output, "w", encoding="utf-8")
            bench.write("filename\tbackend\tmodel\telapsed_sec\tchars\n")

        try:
            for audio_file in filter(is_in_list, audio_files):
                print(f"Transcribing {audio_file.name} [{args.backend}/{args.model}] ...")
                started_at = time.perf_counter()
                text = transcribe_file(
                    backend=args.backend,
                    audio_path=audio_file,
                    model=args.model,
                    language=language,
                    prompt=prompt,
                    client=client,
                )
                elapsed_sec = time.perf_counter() - started_at

                if katakana_converter is not None:
                    text = katakana_converter(text)

                # 改行をスペースに置換
                text = text.replace("\n", " ").strip()
                fo.write(f"{audio_file.name}\t{text}\n")

                if bench is not None:
                    bench.write(
                        f"{audio_file.name}\t{args.backend}\t{args.model}\t"
                        f"{elapsed_sec:.3f}\t{len(text)}\n"
                    )
        finally:
            if bench is not None:
                bench.close()

    print(f"完了: {args.output_tsv}")
    if args.benchmark:
        print(f"ベンチマーク: {benchmark_output}")


if __name__ == "__main__":
    main()
