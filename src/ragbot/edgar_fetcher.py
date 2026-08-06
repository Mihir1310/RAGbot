"""SEC EDGAR API pull script for downloading and parsing financial filings (10-K, 10-Q).

Usage:
    uv run ragbot-edgar --ticker AAPL --form 10-K --count 2
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from ragbot.config import settings


def get_headers() -> dict[str, str]:
    return {"User-Agent": settings.sec_user_agent}


def get_cik_map(client: httpx.Client) -> dict[str, dict]:
    """Fetch ticker to CIK mapping from SEC EDGAR."""
    url = "https://www.sec.gov/files/company_tickers.json"
    res = client.get(url, headers=get_headers())
    res.raise_for_status()
    data = res.json()

    cik_map = {}
    for entry in data.values():
        ticker = entry["ticker"].upper()
        cik_map[ticker] = {
            "cik": str(entry["cik_str"]).zfill(10),
            "cik_num": entry["cik_str"],
            "title": entry["title"],
            "ticker": ticker,
        }
    return cik_map


def clean_html_to_markdown(html_content: str) -> str:
    """Extract clean readable text and tabular markdown from SEC HTML filings."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script, style, XML tags
    for tag in soup(["script", "style", "noscript", "head"]):
        tag.decompose()

    # Process tables into simple text representation
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
            cells = [c for c in cells if c]
            if cells:
                rows.append(" | ".join(cells))
        if rows:
            table_md = "\n" + "\n".join(rows) + "\n"
            table.replace_with(table_md)

    text = soup.get_text(separator="\n", strip=True)
    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def fetch_filings(
    ticker: str,
    form_types: list[str] | None = None,
    max_count: int = 2,
    output_dir: Path | None = None,
) -> list[Path]:
    """Fetch filings for a given company ticker from SEC EDGAR."""
    ticker = ticker.upper()
    form_types = [f.upper() for f in (form_types or ["10-K", "10-Q"])]
    output_dir = output_dir or Path(settings.edgar_data_dir) / ticker
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files: list[Path] = []

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        print(f"Fetching SEC CIK lookup map...")
        cik_map = get_cik_map(client)
        if ticker not in cik_map:
            print(f"Error: Ticker '{ticker}' not found in SEC company database.", file=sys.stderr)
            return []

        company_info = cik_map[ticker]
        cik = company_info["cik"]
        company_title = company_info["title"]
        print(f"Found {ticker} ({company_title}) -> CIK: {cik}")

        # Fetch submissions JSON
        sub_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        print(f"Fetching submissions from SEC API for CIK {cik}...")
        res = client.get(sub_url, headers=get_headers())
        res.raise_for_status()
        submissions = res.json()

        recent = submissions.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accessions = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        filing_dates = recent.get("filingDate", [])
        report_dates = recent.get("reportDate", [])

        count_by_form: dict[str, int] = {f: 0 for f in form_types}

        for i, form in enumerate(forms):
            form_upper = form.upper()
            if form_upper not in form_types:
                continue

            if count_by_form[form_upper] >= max_count:
                continue

            acc_no = accessions[i]
            acc_clean = acc_no.replace("-", "")
            doc_name = primary_docs[i]
            filing_date = filing_dates[i] if i < len(filing_dates) else "unknown"
            report_date = report_dates[i] if i < len(report_dates) else filing_date

            doc_url = f"https://www.sec.gov/Archives/edgar/data/{company_info['cik_num']}/{acc_clean}/{doc_name}"
            print(f"Downloading {ticker} {form_upper} ({filing_date}): {doc_name}...")

            # Respect SEC EDGAR rate limits (<10 requests/sec)
            time.sleep(0.2)
            doc_res = client.get(doc_url, headers=get_headers())
            if doc_res.status_code != 200:
                print(f"Warning: Failed to download {doc_url} (status {doc_res.status_code})", file=sys.stderr)
                continue

            if doc_name.lower().endswith((".htm", ".html")):
                content = clean_html_to_markdown(doc_res.text)
            else:
                content = doc_res.text

            file_stem = f"{form_upper}_{filing_date}_{acc_clean}"
            md_path = output_dir / f"{file_stem}.md"
            json_path = output_dir / f"{file_stem}.json"

            # Prepend filing header to content
            header = f"# {company_title} ({ticker}) - Form {form_upper}\n"
            header += f"**Filing Date:** {filing_date} | **Period End Date:** {report_date} | **Accession:** {acc_no}\n\n"

            md_path.write_text(header + content, encoding="utf-8")

            metadata = {
                "ticker": ticker,
                "company_name": company_title,
                "form_type": form_upper,
                "filing_date": filing_date,
                "report_date": report_date,
                "accession_number": acc_no,
                "source_url": doc_url,
            }
            json_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

            saved_files.append(md_path)
            count_by_form[form_upper] += 1
            print(f"Saved: {md_path}")

            if all(c >= max_count for c in count_by_form.values()):
                break

    return saved_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch SEC EDGAR filings for financial RAGbot.")
    parser.add_argument("--ticker", type=str, default="AAPL", help="Company stock ticker symbol (e.g. AAPL, NVDA, MSFT)")
    parser.add_argument("--form", type=str, nargs="+", default=["10-K", "10-Q"], help="Filing form types (e.g. 10-K 10-Q)")
    parser.add_argument("--count", type=int, default=2, help="Max filings to fetch per form type")
    parser.add_argument("--outdir", type=str, default=None, help="Output directory path")

    args = parser.parse_args()
    outdir = Path(args.outdir) if args.outdir else None
    files = fetch_filings(ticker=args.ticker, form_types=args.form, max_count=args.count, output_dir=outdir)
    print(f"\nCompleted! Downloaded {len(files)} filings for {args.ticker.upper()}.")


if __name__ == "__main__":
    main()
