"""CLI entrypoints for the reporter client."""

from __future__ import annotations

import argparse
from pathlib import Path

from .services.docs_generation_service import DocsGenerationService
from .services.config_service import ConfigService


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(prog="reporter-client")
    parser.add_argument(
        "--config",
        default="reporter_client.yaml",
        help="Path to the YAML configuration file",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_docs = subparsers.add_parser("generate-docs", help="Render MkDocs pages from example payloads and content files")
    generate_docs.add_argument("--examples-dir", default=None, help="Directory containing example JSON payloads")
    generate_docs.add_argument("--content-dir", default=None, help="Directory containing authored Markdown content")
    generate_docs.add_argument("--docs-dir", default=None, help="Target MkDocs docs directory")
    return parser


def main() -> int:
    """Run the requested CLI command."""
    parser = build_parser()
    args = parser.parse_args()
    config = ConfigService().load(Path(args.config))

    if args.command == "generate-docs":
        service = DocsGenerationService(
            examples_dir=Path(args.examples_dir).resolve() if args.examples_dir else config.paths.examples_dir,
            content_dir=Path(args.content_dir).resolve() if args.content_dir else config.paths.content_dir,
            docs_dir=Path(args.docs_dir).resolve() if args.docs_dir else config.paths.docs_dir,
        )
        service.generate()
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
