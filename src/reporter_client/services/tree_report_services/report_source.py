"""Build reusable tree reporting source objects from completed inspection payloads."""

from __future__ import annotations

from collections.abc import Callable

from ...models.tree_report_source import GpsPoint, RiskProfile, TreeGeoJsonSource, TreeImageSource, TreeReportSource


class TreeReportSourceService:
    """Map one completed inspection payload into a reusable reporting source object."""

    def __init__(self, *, completed_form_url_resolver: Callable[[dict], str]) -> None:
        self._completed_form_url_resolver = completed_form_url_resolver

    def build(self, completed_payload: dict, *, transcript: str) -> TreeReportSource:
        form_data = completed_payload.get("form", {}).get("data", {})
        client_tree_details = form_data.get("client_tree_details", {})
        gps = client_tree_details.get("gps", {}) or {}
        main_concerns = _collect_main_concerns(form_data)

        return TreeReportSource(
            project=str(completed_payload.get("project", "")),
            job_id=str(completed_payload.get("job_id", "")),
            client_revision_id=str(completed_payload.get("client_revision_id", "")),
            archived_at=str(completed_payload.get("archived_at", "")),
            species=str(client_tree_details.get("tree_species", "")),
            dbh=client_tree_details.get("dbh"),
            height=client_tree_details.get("height"),
            gps=GpsPoint(
                latitude=_coerce_float(gps.get("latitude")),
                longitude=_coerce_float(gps.get("longitude")),
            ),
            risk_profile=RiskProfile(
                overall_tree_risk=str(form_data.get("overall_tree_risk_rating", {}).get("rating", "")),
                overall_residual_risk=str(form_data.get("overall_residual_risk", {}).get("rating", "")),
                recommended_inspection_interval=str(
                    form_data.get("recommended_inspection_interval", {}).get("text", "")
                ),
            ),
            assessor_name=str(completed_payload.get("profile", {}).get("name", "")),
            main_concerns=main_concerns,
            images=[
                TreeImageSource(
                    image_src=str(image.get("path", "")),
                    caption=str(image.get("caption", "")),
                )
                for image in completed_payload.get("report_images", [])
            ],
            geojson=_build_geojson_source(completed_payload),
            transcript=transcript,
            completed_inspection_form_url=self._completed_form_url_resolver(completed_payload),
        )


def _coerce_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _build_geojson_source(completed_payload: dict) -> TreeGeoJsonSource | None:
    geojson_src = str(
        completed_payload.get("geojson_url")
        or completed_payload.get("final", {}).get("geojson_url")
        or ""
    )
    if not geojson_src:
        return None
    return TreeGeoJsonSource(
        geojson_src=geojson_src,
    )


def _collect_main_concerns(form_data: dict) -> list[str]:
    concerns: list[str] = []
    for section_name in ("crown_and_branches", "trunk", "roots_and_root_collar"):
        value = str(form_data.get(section_name, {}).get("main_concerns", "")).strip()
        if value:
            concerns.append(value)
    return concerns
