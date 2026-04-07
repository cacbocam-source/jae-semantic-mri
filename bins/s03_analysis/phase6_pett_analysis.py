from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from bins.s06_analysis.loaders import (
    extract_epoch_table,
    extract_velocity_table,
    load_metrics,
    summarize_route,
    validate_metrics_payload,
)

STALE_HOURS = 48.0
N_PERMUTATIONS = 2000
N_BOOTSTRAPS = 2000

INFERENTIAL_DIR = Path("analysis_outputs/inferential")
FIGURES_DIR = Path("analysis_outputs/figures")


@dataclass
class RouteSeries:
    route_name: str
    corpus_name: str
    created_at_utc: str
    metric_version: str
    epoch_df: pd.DataFrame
    velocity_df: pd.DataFrame
    summary: dict


def parse_timestamp(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def hours_since(ts: str) -> float:
    created = parse_timestamp(ts)
    now = datetime.now(timezone.utc)
    return (now - created).total_seconds() / 3600.0


def stale_warning(route_name: str, created_at_utc: str) -> str | None:
    age_hours = hours_since(created_at_utc)
    if age_hours > STALE_HOURS:
        return (
            f"[WARN] {route_name} metrics.npz is stale: "
            f"{age_hours:.2f} hours old (created_at_utc={created_at_utc})"
        )
    return None


def parse_epoch_label(label: str) -> tuple[int, int]:
    start_str, end_str = label.split("-")
    return int(start_str), int(end_str)


def bootstrap_ci(
    sample_a: np.ndarray,
    sample_b: np.ndarray | None = None,
    statistic=None,
    n_bootstraps: int = N_BOOTSTRAPS,
    rng: np.random.Generator | None = None,
) -> tuple[float, float]:
    if rng is None:
        rng = np.random.default_rng(42)

    estimates: list[float] = []

    if sample_b is None:
        for _ in range(n_bootstraps):
            draw_a = rng.choice(sample_a, size=len(sample_a), replace=True)
            estimates.append(float(statistic(draw_a)))
    else:
        for _ in range(n_bootstraps):
            draw_a = rng.choice(sample_a, size=len(sample_a), replace=True)
            draw_b = rng.choice(sample_b, size=len(sample_b), replace=True)
            estimates.append(float(statistic(draw_a, draw_b)))

    low, high = np.percentile(estimates, [2.5, 97.5])
    return float(low), float(high)


def permutation_p_value(
    sample_a: np.ndarray,
    sample_b: np.ndarray,
    observed_stat: float,
    statistic=None,
    n_permutations: int = N_PERMUTATIONS,
    rng: np.random.Generator | None = None,
) -> float:
    if rng is None:
        rng = np.random.default_rng(42)

    pooled = np.concatenate([sample_a, sample_b])
    n_a = len(sample_a)
    exceed = 0

    for _ in range(n_permutations):
        shuffled = rng.permutation(pooled)
        perm_a = shuffled[:n_a]
        perm_b = shuffled[n_a:]
        perm_stat = float(statistic(perm_a, perm_b))
        if abs(perm_stat) >= abs(observed_stat):
            exceed += 1

    return float((exceed + 1) / (n_permutations + 1))


def load_route_series(route_name: str) -> RouteSeries:
    metrics = load_metrics(route_name)
    validate_metrics_payload(metrics)

    epoch_df = pd.DataFrame(extract_epoch_table(metrics))
    epoch_bounds = epoch_df["epoch"].map(parse_epoch_label)
    epoch_df["start_year"] = [start for start, _ in epoch_bounds]
    epoch_df["end_year"] = [end for _, end in epoch_bounds]
    epoch_df["mid_year"] = (epoch_df["start_year"] + epoch_df["end_year"]) / 2.0
    epoch_df["epoch_index"] = np.arange(len(epoch_df))

    velocity_df = pd.DataFrame(extract_velocity_table(metrics))
    velocity_df["transition_index"] = np.arange(len(velocity_df))

    return RouteSeries(
        route_name=str(metrics["route_name"]),
        corpus_name=str(metrics["corpus_name"]),
        created_at_utc=str(metrics["created_at_utc"]),
        metric_version=str(metrics["metric_version"]),
        epoch_df=epoch_df,
        velocity_df=velocity_df,
        summary=summarize_route(route_name),
    )


def candidate_break_indices(n_points: int) -> list[int]:
    return [idx for idx in range(1, n_points - 2 + 1) if (idx + 1) >= 2 and (n_points - idx - 1) >= 2]


def segmented_fit(x: np.ndarray, y: np.ndarray, break_idx: int) -> dict:
    pre_x = x[: break_idx + 1]
    pre_y = y[: break_idx + 1]
    post_x = x[break_idx + 1 :]
    post_y = y[break_idx + 1 :]

    pre_slope, pre_intercept = np.polyfit(pre_x, pre_y, 1)
    post_slope, post_intercept = np.polyfit(post_x, post_y, 1)

    pre_pred = pre_slope * pre_x + pre_intercept
    post_pred = post_slope * post_x + post_intercept

    sse_pre = float(np.sum((pre_y - pre_pred) ** 2))
    sse_post = float(np.sum((post_y - post_pred) ** 2))
    sse_total = sse_pre + sse_post

    effect_size = float(np.mean(post_y) - np.mean(pre_y))

    return {
        "break_idx": int(break_idx),
        "pre_n": int(len(pre_y)),
        "post_n": int(len(post_y)),
        "pre_slope": float(pre_slope),
        "post_slope": float(post_slope),
        "pre_intercept": float(pre_intercept),
        "post_intercept": float(post_intercept),
        "sse_total": sse_total,
        "effect_size": effect_size,
        "pre_values": pre_y,
        "post_values": post_y,
    }


def primary_break_index(route: RouteSeries) -> int | None:
    df = route.epoch_df.reset_index(drop=True)
    for idx in range(len(df) - 1):
        if int(df.loc[idx, "end_year"]) == 1994 and int(df.loc[idx + 1, "start_year"]) == 1995:
            return idx
    return None


def breakpoint_row(route: RouteSeries, label: str, fit: dict, p_value: float, ci_low: float, ci_high: float) -> dict:
    df = route.epoch_df.reset_index(drop=True)
    break_idx = fit["break_idx"]
    left_epoch = str(df.loc[break_idx, "epoch"])
    right_epoch = str(df.loc[break_idx + 1, "epoch"])

    return {
        "route_name": route.route_name,
        "analysis": label,
        "left_epoch": left_epoch,
        "right_epoch": right_epoch,
        "break_index": int(break_idx),
        "pre_n": int(fit["pre_n"]),
        "post_n": int(fit["post_n"]),
        "pre_slope": float(fit["pre_slope"]),
        "post_slope": float(fit["post_slope"]),
        "sse_total": float(fit["sse_total"]),
        "effect_size_mean_diff": float(fit["effect_size"]),
        "p_value": float(p_value),
        "ci_low": float(ci_low),
        "ci_high": float(ci_high),
    }


def run_breakpoint_analyses(route: RouteSeries) -> list[dict]:
    df = route.epoch_df.reset_index(drop=True)
    x = df["mid_year"].to_numpy(dtype=float)
    y = df["dispersion"].to_numpy(dtype=float)

    results: list[dict] = []
    rng = np.random.default_rng(42)
    stat_fn = lambda a, b: np.mean(b) - np.mean(a)

    primary_idx = primary_break_index(route)
    if primary_idx is not None:
        pre_values = y[: primary_idx + 1]
        post_values = y[primary_idx + 1 :]
        observed = float(np.mean(post_values) - np.mean(pre_values))
        p_value = permutation_p_value(
            pre_values,
            post_values,
            observed,
            statistic=stat_fn,
            rng=rng,
        )
        ci_low, ci_high = bootstrap_ci(
            pre_values,
            post_values,
            statistic=stat_fn,
            rng=rng,
        )

        primary_row = {
            "route_name": route.route_name,
            "analysis": "primary_breakpoint",
            "left_epoch": str(df.loc[primary_idx, "epoch"]),
            "right_epoch": str(df.loc[primary_idx + 1, "epoch"]),
            "break_index": int(primary_idx),
            "pre_n": int(len(pre_values)),
            "post_n": int(len(post_values)),
            "pre_slope": None,
            "post_slope": None,
            "sse_total": None,
            "effect_size_mean_diff": observed,
            "p_value": float(p_value),
            "ci_low": float(ci_low),
            "ci_high": float(ci_high),
        }

        if len(pre_values) >= 2 and len(post_values) >= 2:
            fit = segmented_fit(x, y, primary_idx)
            primary_row["pre_slope"] = float(fit["pre_slope"])
            primary_row["post_slope"] = float(fit["post_slope"])
            primary_row["sse_total"] = float(fit["sse_total"])

        results.append(primary_row)
    else:
        results.append(
            {
                "route_name": route.route_name,
                "analysis": "primary_breakpoint",
                "left_epoch": None,
                "right_epoch": None,
                "break_index": None,
                "pre_n": None,
                "post_n": None,
                "pre_slope": None,
                "post_slope": None,
                "sse_total": None,
                "effect_size_mean_diff": None,
                "p_value": None,
                "ci_low": None,
                "ci_high": None,
            }
        )

    candidates = candidate_break_indices(len(df))
    if candidates:
        fits = [segmented_fit(x, y, idx) for idx in candidates]
        best_fit = sorted(fits, key=lambda item: item["sse_total"])[0]
        p_value = permutation_p_value(
            best_fit["pre_values"],
            best_fit["post_values"],
            best_fit["effect_size"],
            statistic=stat_fn,
            rng=rng,
        )
        ci_low, ci_high = bootstrap_ci(
            best_fit["pre_values"],
            best_fit["post_values"],
            statistic=stat_fn,
            rng=rng,
        )
        results.append(breakpoint_row(route, "sensitivity_best_break", best_fit, p_value, ci_low, ci_high))

    return results

def velocity_significance(route: RouteSeries) -> dict:
    values = route.velocity_df["velocity"].to_numpy(dtype=float)
    observed = float(np.mean(values))
    rng = np.random.default_rng(42)

    exceed = 0
    for _ in range(N_PERMUTATIONS):
        signs = rng.choice([-1.0, 1.0], size=len(values), replace=True)
        perm_stat = float(np.mean(values * signs))
        if abs(perm_stat) >= abs(observed):
            exceed += 1
    p_value = float((exceed + 1) / (N_PERMUTATIONS + 1))

    ci_low, ci_high = bootstrap_ci(values, statistic=np.mean, rng=rng)

    return {
        "analysis": "velocity_significance",
        "route_name": route.route_name,
        "effect_size": observed,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "n": int(len(values)),
    }


def era_comparison(legacy: RouteSeries, modern: RouteSeries) -> dict:
    legacy_vals = legacy.epoch_df["dispersion"].to_numpy(dtype=float)
    modern_vals = modern.epoch_df["dispersion"].to_numpy(dtype=float)
    observed = float(np.mean(modern_vals) - np.mean(legacy_vals))
    stat_fn = lambda a, b: np.mean(b) - np.mean(a)
    rng = np.random.default_rng(42)

    p_value = permutation_p_value(
        legacy_vals,
        modern_vals,
        observed,
        statistic=stat_fn,
        rng=rng,
    )
    ci_low, ci_high = bootstrap_ci(
        legacy_vals,
        modern_vals,
        statistic=stat_fn,
        rng=rng,
    )

    return {
        "analysis": "era_comparison_dispersion",
        "route_name": "Route_B_Legacy_vs_Route_A_Modern",
        "effect_size": observed,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "legacy_n": int(len(legacy_vals)),
        "modern_n": int(len(modern_vals)),
    }


def modern_monotonic_trend(modern: RouteSeries) -> dict:
    x = modern.epoch_df["mid_year"].to_numpy(dtype=float)
    y = modern.epoch_df["dispersion"].to_numpy(dtype=float)

    tau, p_value = stats.kendalltau(x, y)

    slope, intercept, low_slope, high_slope = stats.theilslopes(y, x, 0.95)

    return {
        "analysis": "modern_monotonic_trend",
        "route_name": modern.route_name,
        "effect_size": float(slope),
        "p_value": float(1.0 if np.isnan(p_value) else p_value),
        "ci_low": float(low_slope),
        "ci_high": float(high_slope),
        "n": int(len(x)),
        "tau": float(0.0 if np.isnan(tau) else tau),
        "intercept": float(intercept),
        "effect_metric": "theil_sen_slope_per_year",
        "p_metric": "kendall_tau_pvalue",
        "ci_metric": "theil_sen_95ci",
    }

def write_route_figure(route: RouteSeries, breakpoint_results: list[dict]) -> Path:
    df = route.epoch_df.reset_index(drop=True)
    x = df["mid_year"].to_numpy(dtype=float)
    y = df["dispersion"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, marker="o")
    ax.set_title(f"{route.route_name} PETT / segmented regression")
    ax.set_xlabel("Epoch midpoint year")
    ax.set_ylabel("Semantic dispersion")

    for result in breakpoint_results:
        if result["analysis"] != "sensitivity_best_break":
            continue
        if result["break_index"] is None:
            continue
        break_idx = int(result["break_index"])
        left_x = x[break_idx]
        right_x = x[break_idx + 1]
        ax.axvline((left_x + right_x) / 2.0, linestyle="--")

    output_path = FIGURES_DIR / f"{route.route_name}_phase6_pett_dispersion.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def write_markdown_report(
    route_breaks: list[dict],
    secondary_results: list[dict],
    stale_messages: list[str],
) -> Path:
    output_path = INFERENTIAL_DIR / "phase6_pett_report.md"

    lines: list[str] = []
    lines.append("# Phase 6 Track B — PETT / Segmented Regression Report")
    lines.append("")
    lines.append("## Metrics freshness warnings")
    lines.append("")
    if stale_messages:
        for msg in stale_messages:
            lines.append(f"- {msg}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Breakpoint analyses")
    lines.append("")
    for row in route_breaks:
        lines.append(
            f"- {row['route_name']} | {row['analysis']} | "
            f"left_epoch={row['left_epoch']} | right_epoch={row['right_epoch']} | "
            f"effect={row['effect_size_mean_diff']} | p={row['p_value']} | "
            f"95% CI=[{row['ci_low']}, {row['ci_high']}]"
        )
    lines.append("")
    lines.append("## Secondary analyses")
    lines.append("")
    for row in secondary_results:
        lines.append(
            f"- {row['analysis']} | {row['route_name']} | "
            f"effect={row['effect_size']} | p={row['p_value']} | "
            f"95% CI=[{row['ci_low']}, {row['ci_high']}]"
        )
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def ensure_output_dirs() -> None:
    INFERENTIAL_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    ensure_output_dirs()

    routes = [load_route_series("Route_A_Modern"), load_route_series("Route_B_Legacy")]

    stale_messages = []
    for route in routes:
        warning_msg = stale_warning(route.route_name, route.created_at_utc)
        if warning_msg:
            print(warning_msg)
            stale_messages.append(warning_msg)

    breakpoint_rows: list[dict] = []
    for route in routes:
        route_rows = run_breakpoint_analyses(route)
        breakpoint_rows.extend(route_rows)
        figure_path = write_route_figure(route, route_rows)
        print(f"[OK] figure={figure_path}")

    secondary_rows = [
        velocity_significance(routes[0]),
        velocity_significance(routes[1]),
        era_comparison(routes[1], routes[0]),
        modern_monotonic_trend(routes[0]),
    ]

    breakpoint_df = pd.DataFrame(breakpoint_rows)
    breakpoint_path = INFERENTIAL_DIR / "phase6_pett_breakpoints.csv"
    breakpoint_df.to_csv(breakpoint_path, index=False)
    print(f"[OK] csv={breakpoint_path}")

    secondary_df = pd.DataFrame(secondary_rows)
    secondary_path = INFERENTIAL_DIR / "phase6_pett_secondary_tests.csv"
    secondary_df.to_csv(secondary_path, index=False)
    print(f"[OK] csv={secondary_path}")

    report_path = write_markdown_report(breakpoint_rows, secondary_rows, stale_messages)
    print(f"[OK] report={report_path}")


if __name__ == "__main__":
    main()
