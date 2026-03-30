"""CLI entrypoints for the reporter client."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .cli_logging import configure_logging
from .services.docs_generation_service import DocsGenerationService
from .services.basemap_service import BasemapService, BoundingBox
from .services.config_service import ConfigService
from .services.publication_execution_service import PublicationExecutionService


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(prog="reporter-client")
    parser.add_argument(
        "--config",
        default="reporter_client.yaml",
        help="Path to the YAML configuration file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose CLI logging",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_docs = subparsers.add_parser("generate-docs", help="Render MkDocs pages from example payloads and content files")
    generate_docs.add_argument("--examples-dir", default=None, help="Directory containing example JSON payloads")
    generate_docs.add_argument("--content-dir", default=None, help="Directory containing authored Markdown content")
    generate_docs.add_argument("--docs-dir", default=None, help="Target MkDocs docs directory")
    subparsers.add_parser("publish-staged", help="Incrementally publish from staged job bundles using the local publish index")
    build_basemap = subparsers.add_parser("build-basemap", help="Build a project basemap from an exact bounding box")
    build_basemap.add_argument("--slug", required=True, help="Output slug, for example briarwood")
    build_basemap.add_argument("--west", required=True, type=float, help="Bounding box west longitude")
    build_basemap.add_argument("--east", required=True, type=float, help="Bounding box east longitude")
    build_basemap.add_argument("--south", required=True, type=float, help="Bounding box south latitude")
    build_basemap.add_argument("--north", required=True, type=float, help="Bounding box north latitude")
    build_basemap.add_argument("--zoom", type=int, default=BasemapService.DEFAULT_ZOOM, help="OSM zoom level")
    build_basemap.add_argument("--docs-dir", default=None, help="Target MkDocs docs directory")
    return parser


def main() -> int:
    """Run the requested CLI command."""
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(verbose=args.verbose)
    logger = logging.getLogger("reporter_client.cli")
    config = ConfigService().load(Path(args.config))

    if args.command == "generate-docs":
        logger.info("starting generate-docs")
        service = DocsGenerationService(
            staging_root=config.staging.root,
            content_dir=Path(args.content_dir).resolve() if args.content_dir else config.paths.content_dir,
            docs_dir=Path(args.docs_dir).resolve() if args.docs_dir else config.paths.docs_dir,
        )
        service.generate()
        logger.info("generate-docs complete")
        return 0

    if args.command == "publish-staged":
        logger.info("starting publish-staged")
        service = PublicationExecutionService(
            staging_root=config.staging.root,
            content_dir=config.paths.content_dir,
            docs_dir=config.paths.docs_dir,
            index_path=config.publish.index_path,
        )
        service.run()
        logger.info("publish-staged complete")
        return 0

    if args.command == "build-basemap":
        logger.info("starting build-basemap for %s", args.slug)
        service = BasemapService()
        service.build(
            docs_dir=Path(args.docs_dir).resolve() if args.docs_dir else config.paths.docs_dir,
            slug=args.slug,
            bbox=BoundingBox(
                west=args.west,
                east=args.east,
                south=args.south,
                north=args.north,
            ),
            zoom=args.zoom,
        )
        logger.info("build-basemap complete for %s", args.slug)
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
