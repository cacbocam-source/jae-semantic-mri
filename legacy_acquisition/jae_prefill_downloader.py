from __future__ import annotations

import argparse
import hashlib
import random
import re
import time
import urllib.parse
import warnings
from collections import deque
from dataclasses import replace
from html import unescape
from pathlib import Path
from typing import Final, Iterable

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import SSLError
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.retry import Retry

from jae_legacy_acquisition_contract import (
    DOWNLOAD_DOWNLOADED,
    DOWNLOAD_FAILED,
    DOWNLOAD_SKIPPED,
    PROJECT_ROOT_DEFAULT,
    STATUS_CONFIRMED,
    PrefillRecord,
    ensure_project_root,
    read_prefill_csv,
    resolve_under_project_root,
    utc_now_iso,
    write_prefill_csv,
)

warnings.simplefilter("ignore", InsecureRequestWarning)

META_PDF_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']',
        re.I,
    ),
    re.compile(
        r'<meta[^>]+property=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']',
        re.I,
    ),
)
META_TITLE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r'<meta[^>]+name=["\']citation_title["\'][^>]+content=["\']([^"\']+)["\']',
        re.I,
    ),
    re.compile(
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
        re.I,
    ),
)
H1_TITLE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r'<h1[^>]*class=["\'][^"\']*title[^"\']*["\'][^>]*>(.*?)</h1>',
    re.I | re.S,
)
ARTICLE_PDF_LINK_PATTERN: Final[re.Pattern[str]] = re.compile(
    r'href=["\']([^"\']*(?:article/download|article/view|download)[^"\']*\.pdf[^"\']*|'
    r'[^"\']*/article/download/[^"\']+|'
    r'[^"\']*\.pdf)["\']',
    re.I,
)


class RequestGuard:
    def __init__(
        self,
        *,
        min_gap_seconds: float = 2.0,
        session_cap_per_minute: int = 20,
        jitter_seconds: float = 0.2,
    ) -> None:
        self.min_gap_seconds = min_gap_seconds
        self.session_cap_per_minute = session_cap_per_minute
        self.jitter_seconds = jitter_seconds
        self._session_times: deque[float] = deque()
        self._domain_last_seen: dict[str, float] = {}

    def wait_for_slot(self, domain: str) -> None:
        now = time.monotonic()
        cutoff = now - 60.0
        while self._session_times and self._session_times[0] < cutoff:
            self._session_times.popleft()

        if len(self._session_times) >= self.session_cap_per_minute:
            wait_for = 60.0 - (now - self._session_times[0])
            if wait_for > 0:
                print(
                    f"[INFO] Session rate cap ({self.session_cap_per_minute} req/min) "
                    f"reached — waiting {wait_for:.1f}s."
                )
                time.sleep(wait_for)

        last_seen = self._domain_last_seen.get(domain)
        if last_seen is not None:
            delta = now - last_seen
            wait_for = self.min_gap_seconds - delta
            if wait_for > 0:
                time.sleep(wait_for + random.uniform(0, self.jitter_seconds))

        current = time.monotonic()
        self._session_times.append(current)
        self._domain_last_seen[domain] = current


def append_note(existing: str, new_note: str) -> str:
    existing = (existing or "").strip()
    new_note = (new_note or "").strip()
    if not new_note:
        return existing
    if not existing:
        return new_note
    if new_note in existing:
        return existing
    return f"{existing}; {new_note}"


def build_session() -> requests.Session:
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": "JAE_Legacy_Audit/legacy-prefill-downloader (+research workflow)",
            "Accept": "text/html,application/pdf,application/xhtml+xml;q=0.9,*/*;q=0.8",
        }
    )
    return session


def request_with_ssl_fallback(
    *,
    session: requests.Session,
    url: str,
    guard: RequestGuard,
    timeout: int,
    stream: bool = False,
) -> tuple[requests.Response, str]:
    domain = urllib.parse.urlparse(url).netloc
    guard.wait_for_slot(domain)
    try:
        response = session.get(url, timeout=timeout, stream=stream, allow_redirects=True)
        return response, "STRICT_SSL"
    except SSLError:
        guard.wait_for_slot(domain)
        response = session.get(
            url,
            timeout=timeout,
            stream=stream,
            allow_redirects=True,
            verify=False,
        )
        return response, "INSECURE_SSL_FALLBACK"


def extract_first(patterns: Iterable[re.Pattern[str]], html: str) -> str:
    for pattern in patterns:
        match = pattern.search(html)
        if match:
            return unescape(match.group(1)).strip()
    return ""


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return unescape(value).strip()


def absolutize(base_url: str, maybe_relative: str) -> str:
    return urllib.parse.urljoin(base_url, maybe_relative.strip())


def parse_landing_page(html: str, base_url: str) -> tuple[str, str, str]:
    pdf_url = extract_first(META_PDF_PATTERNS, html)
    if not pdf_url:
        match = ARTICLE_PDF_LINK_PATTERN.search(html)
        if match:
            pdf_url = match.group(1).strip()
    if pdf_url:
        pdf_url = absolutize(base_url, pdf_url)

    title = extract_first(META_TITLE_PATTERNS, html)
    if not title:
        match = H1_TITLE_PATTERN.search(html)
        if match:
            title = strip_tags(match.group(1))

    source_identifier = ""
    parsed = urllib.parse.urlparse(base_url)
    if "/index.php/" in parsed.path:
        source_identifier = parsed.path.split("/index.php/")[-1].strip("/")

    return pdf_url, title, source_identifier


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_probable_direct_pdf_url(url: str) -> bool:
    value = (url or "").strip().lower()
    if not value:
        return False
    if value.endswith(".pdf"):
        return True
    if "/article/download/" in value:
        return True
    return False


def response_looks_like_pdf(response: requests.Response) -> bool:
    content_type = (response.headers.get("Content-Type") or "").lower()
    final_url = str(response.url).lower()
    if "application/pdf" in content_type:
        return True
    if final_url.endswith(".pdf"):
        return True
    if "/article/download/" in final_url:
        return True
    return False


def choose_initial_download_target(record: PrefillRecord) -> tuple[str, str]:
    """
    Precedence:
    1. pdf_url exists -> direct download
    2. article_landing_url contains /article/download/ or endswith .pdf -> direct
    3. crossref_url exists -> inspect DOI/crossref target
    4. article_landing_url exists -> landing-page parse
    5. source_url direct -> direct, else landing-page parse
    """
    pdf_url = (record.pdf_url or "").strip()
    article_url = (record.article_landing_url or "").strip()
    crossref_url = (record.crossref_url or "").strip()
    source_url = (record.source_url or "").strip()

    if pdf_url:
        return pdf_url, "direct_pdf_url"

    if is_probable_direct_pdf_url(article_url):
        return article_url, "direct_article_download_url"

    if crossref_url:
        return crossref_url, "doi_or_crossref_url"

    if article_url:
        return article_url, "landing_page_parse"

    if is_probable_direct_pdf_url(source_url):
        return source_url, "direct_source_url"

    if source_url:
        return source_url, "landing_page_parse"

    return "", "no_usable_url"


def derive_target_url(record: PrefillRecord) -> str:
    target, _ = choose_initial_download_target(record)
    return target


def should_attempt(record: PrefillRecord, include_pending: bool) -> bool:
    if record.download_status in {DOWNLOAD_DOWNLOADED, DOWNLOAD_SKIPPED}:
        return False
    if not include_pending and record.manual_review_status != STATUS_CONFIRMED:
        return False
    return bool(derive_target_url(record))


def stream_response_to_path(response: requests.Response, destination: Path) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = destination.with_suffix(destination.suffix + ".part")
    byte_count = 0
    with tmp_path.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=1024 * 64):
            if not chunk:
                continue
            handle.write(chunk)
            byte_count += len(chunk)
    tmp_path.replace(destination)
    return byte_count


def write_bytes_to_path(content: bytes, destination: Path) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return len(content)


def download_binary_to_path(
    *,
    session: requests.Session,
    url: str,
    guard: RequestGuard,
    destination: Path,
    timeout: int,
) -> tuple[int, int, str, str]:
    response, ssl_mode = request_with_ssl_fallback(
        session=session,
        url=url,
        guard=guard,
        timeout=timeout,
        stream=True,
    )
    with response:
        response.raise_for_status()
        byte_count = stream_response_to_path(response, destination)
        return response.status_code, byte_count, str(response.url), ssl_mode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download confirmed legacy/modern prefill rows into the JAE_Legacy_Audit staging area."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--csv-path", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--include-pending", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--min-gap-seconds", type=float, default=2.0)
    parser.add_argument("--session-cap-per-minute", type=int, default=20)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_root = ensure_project_root(args.project_root)
    csv_path = args.csv_path.resolve()
    records = read_prefill_csv(csv_path)
    session = build_session()
    guard = RequestGuard(
        min_gap_seconds=args.min_gap_seconds,
        session_cap_per_minute=args.session_cap_per_minute,
    )

    updated_records: list[PrefillRecord] = []

    for record in records:
        mutable = replace(record)
        if not should_attempt(record, args.include_pending):
            updated_records.append(mutable)
            continue

        target_url, strategy = choose_initial_download_target(record)
        destination_relative = (
            record.destination_stage_path
            or record.staged_pdf_path
            or record.destination_stage_path
        )
        destination_path = resolve_under_project_root(project_root, destination_relative)

        if args.dry_run:
            print(
                f"[DRY-RUN] {record.record_id} "
                f"strategy={strategy} -> {target_url} -> {destination_path}"
            )
            updated_records.append(mutable)
            continue

        try:
            final_url = target_url
            title = (record.article_title or "").strip()
            source_identifier = (record.source_identifier or "").strip()

            if strategy in {
                "direct_pdf_url",
                "direct_article_download_url",
                "direct_source_url",
            }:
                http_status, downloaded_bytes, final_url, ssl_mode = download_binary_to_path(
                    session=session,
                    url=target_url,
                    guard=guard,
                    destination=destination_path,
                    timeout=args.timeout,
                )
                mutable.notes = append_note(mutable.notes, f"DOWNLOAD_STRATEGY={strategy}")
                mutable.notes = append_note(mutable.notes, f"download_ssl={ssl_mode}")

            elif strategy in {"doi_or_crossref_url", "landing_page_parse"}:
                response, ssl_mode = request_with_ssl_fallback(
                    session=session,
                    url=target_url,
                    guard=guard,
                    timeout=args.timeout,
                    stream=False,
                )
                with response:
                    response.raise_for_status()
                    mutable.notes = append_note(mutable.notes, f"landing_ssl={ssl_mode}")

                    if response_looks_like_pdf(response):
                        http_status = response.status_code
                        downloaded_bytes = write_bytes_to_path(response.content, destination_path)
                        final_url = str(response.url)
                        mutable.notes = append_note(
                            mutable.notes,
                            f"DOWNLOAD_STRATEGY={strategy}_resolved_direct_pdf",
                        )
                    else:
                        html = response.text
                        final_url = str(response.url)
                        parsed_pdf_url, parsed_title, parsed_identifier = parse_landing_page(
                            html,
                            final_url,
                        )
                        if parsed_title and not title:
                            title = parsed_title
                        if parsed_identifier and not source_identifier:
                            source_identifier = parsed_identifier

                        if not parsed_pdf_url:
                            raise ValueError(
                                f"No PDF URL discovered from landing page: {final_url}"
                            )

                        http_status, downloaded_bytes, final_url, ssl_mode = download_binary_to_path(
                            session=session,
                            url=parsed_pdf_url,
                            guard=guard,
                            destination=destination_path,
                            timeout=args.timeout,
                        )
                        mutable.notes = append_note(
                            mutable.notes,
                            f"DOWNLOAD_STRATEGY={strategy}_parsed_pdf_link",
                        )
                        mutable.notes = append_note(mutable.notes, f"download_ssl={ssl_mode}")
            else:
                raise ValueError(f"No usable URL for record {record.record_id}")

            checksum = sha256_file(destination_path)

            if is_probable_direct_pdf_url(final_url):
                mutable.pdf_url = final_url
            mutable.article_title = title or mutable.article_title
            mutable.source_identifier = source_identifier or mutable.source_identifier
            mutable.staged_pdf_path = str(destination_path)
            mutable.download_status = DOWNLOAD_DOWNLOADED
            mutable.download_date = utc_now_iso()
            mutable.download_http_status = str(http_status)
            mutable.downloaded_bytes = str(downloaded_bytes)
            mutable.checksum_sha256 = checksum
            mutable.source_url = final_url or target_url

            print(f"[OK] {mutable.record_id} -> {destination_path}")

        except Exception as exc:
            mutable.download_status = DOWNLOAD_FAILED
            mutable.notes = append_note(
                mutable.notes,
                f"download_error={type(exc).__name__}:{exc}",
            )
            print(f"[FAIL] {mutable.record_id}: {exc}")

        updated_records.append(mutable)

    write_prefill_csv(updated_records, csv_path)
    print(f"Updated CSV: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())