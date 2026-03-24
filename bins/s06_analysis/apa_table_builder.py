from __future__ import annotations

from pathlib import Path

from bins.s06_analysis.loaders import (
    extract_epoch_table,
    extract_velocity_table,
    load_metrics,
    summarize_route,
)

APA_TABLES_DIR = Path("manuscript/paper/tables")
APA_TABLES_DIR.mkdir(parents=True, exist_ok=True)


def _format_plain_table(headers: list[str], rows: list[list[str]]) -> str:
    widths: list[int] = []
    for i, header in enumerate(headers):
        cell_width = max((len(row[i]) for row in rows), default=0)
        widths.append(max(len(header), cell_width))

    header_line = "  ".join(header.ljust(widths[i]) for i, header in enumerate(headers))
    rule_line = "  ".join("-" * widths[i] for i in range(len(headers)))

    body_lines = []
    for row in rows:
        body_lines.append("  ".join(row[i].ljust(widths[i]) for i in range(len(headers))))

    return "\n".join([header_line, rule_line, *body_lines])


def _route_epoch_note_fragment(route_name: str) -> str:
    summary = summarize_route(route_name)
    labels = ", ".join(summary["epoch_labels"])
    epoch_count = summary["epoch_count"]
    return f"{route_name} spans {epoch_count} epochs ({labels})"


def _route_transition_note_fragment(route_name: str) -> str:
    summary = summarize_route(route_name)
    transition_count = len(extract_velocity_table(load_metrics(route_name)))
    if transition_count == 0:
        return f"{route_name} contributes no adjacent-epoch transitions"
    if transition_count == 1:
        return f"{route_name} contributes 1 adjacent-epoch transition"
    return f"{route_name} contributes {transition_count} adjacent-epoch transitions"


def build_table_1_epoch_summary() -> Path:
    routes = ["Route_A_Modern", "Route_B_Legacy"]

    rows: list[list[str]] = []
    for route_name in routes:
        summary = summarize_route(route_name)
        metrics = load_metrics(route_name)
        epoch_rows = extract_epoch_table(metrics)

        for row in epoch_rows:
            rows.append(
                [
                    summary["route_name"],
                    summary["corpus_name"],
                    row["epoch"],
                    str(row["count"]),
                    f"{row['dispersion']:.3f}",
                ]
            )

    epoch_note = "; ".join(_route_epoch_note_fragment(route_name) for route_name in routes)

    content = "\n".join(
        [
            "**Table 1**",
            "*Epoch-Level Descriptive Summary by Route*",
            "",
            _format_plain_table(
                headers=[
                    "Route",
                    "Corpus",
                    "Epoch",
                    "n",
                    "Semantic dispersion",
                ],
                rows=rows,
            ),
            "",
            (
                "Note. Values are descriptive summaries derived from validated route-level metrics. "
                "Semantic dispersion values are rounded to three decimals. "
                f"In the current validated state, {epoch_note}."
            ),
            "",
        ]
    )

    output_path = APA_TABLES_DIR / "Table_1_epoch_summary.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def build_table_2_innovation_velocity() -> Path:
    routes = ["Route_A_Modern", "Route_B_Legacy"]

    rows: list[list[str]] = []
    transition_fragments: list[str] = []

    for route_name in routes:
        summary = summarize_route(route_name)
        metrics = load_metrics(route_name)
        velocity_rows = extract_velocity_table(metrics)

        transition_count = len(velocity_rows)
        if transition_count == 0:
            transition_fragments.append(f"{route_name} contributes no adjacent-epoch transitions")
        elif transition_count == 1:
            transition_fragments.append(f"{route_name} contributes 1 adjacent-epoch transition")
        else:
            transition_fragments.append(
                f"{route_name} contributes {transition_count} adjacent-epoch transitions"
            )

        for row in velocity_rows:
            rows.append(
                [
                    summary["route_name"],
                    summary["corpus_name"],
                    row["transition"],
                    f"{row['velocity']:.3f}",
                ]
            )

    transition_note = "; ".join(transition_fragments)

    content = "\n".join(
        [
            "**Table 2**",
            "*Route-Internal Innovation Velocity by Adjacent Epoch Transition*",
            "",
            _format_plain_table(
                headers=[
                    "Route",
                    "Corpus",
                    "Transition",
                    "Innovation velocity",
                ],
                rows=rows,
            ),
            "",
            (
                "Note. Innovation velocity is reported only where adjacent epoch transitions exist. "
                "Values are rounded to three decimals. "
                f"In the current validated state, {transition_note}."
            ),
            "",
        ]
    )

    output_path = APA_TABLES_DIR / "Table_2_innovation_velocity.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def run() -> None:
    try:
        table_1 = build_table_1_epoch_summary()
        print(f"[APA TABLE] {table_1}")
    except Exception as exc:
        print(f"[FAIL] Table 1: {exc}")

    try:
        table_2 = build_table_2_innovation_velocity()
        print(f"[APA TABLE] {table_2}")
    except Exception as exc:
        print(f"[FAIL] Table 2: {exc}")


if __name__ == "__main__":
    run()