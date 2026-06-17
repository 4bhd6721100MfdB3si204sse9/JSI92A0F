from __future__ import annotations

import argparse
import sys
from pathlib import Path

from deepwiki_triage import save_deepwiki_response


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Route copied/exported DeepWiki output into Sentinel staging folders.")
    parser.add_argument("input", help="DeepWiki response file")
    parser.add_argument("--source-url", default="manual://deepwiki")
    parser.add_argument("--prefix", default="sentinel")
    args = parser.parse_args(argv)

    content = Path(args.input).read_text(encoding="utf-8")
    saved = save_deepwiki_response(content, args.source_url, prefix=args.prefix)
    print(f"saved={saved}" if saved else "saved=None")
    return 0


if __name__ == "__main__":
    sys.exit(main())

