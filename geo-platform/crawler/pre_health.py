import re
import requests
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Paths anchored to your repo layout (see screenshot)
#   GEO/
#     client docs/
#       context.md
#       health_checks/
#     geo-platform/
#       crawler/
#         pre_health.py  (this file)
# ──────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent                  # .../GEO/geo-platform/crawler
REPO_ROOT  = SCRIPT_DIR.parent.parent                         # .../GEO
CLIENT_DOCS_DIR = REPO_ROOT / "client docs"                   # .../GEO/client docs
INTAKE_MD  = CLIENT_DOCS_DIR / "context.md"                   # .../GEO/client docs/context.md
OUTPUT_DIR = CLIENT_DOCS_DIR / "health_checks"                # .../GEO/client docs/health_checks

# ──────────────────────────────────────────────────────────────────────────────
# Intake extractors
# ──────────────────────────────────────────────────────────────────────────────

def extract_domain_from_md(filepath: Path) -> str | None:
    """Extract the first domain URL from the intake .md file."""
    text = filepath.read_text(encoding="utf-8")
    m = re.search(r"https?://[^\s`]+", text)
    return m.group(0) if m else None

def extract_cms_from_md(filepath: Path) -> str | None:
    """
    Extract the CMS from the fenced code block under the heading:
      ### **CMS**
      ```
      Squarespace
      ```
    """
    md = filepath.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^###\s*\*\*CMS\*\*\s*```(?:[a-zA-Z0-9_-]*)?\s*([\s\S]*?)\s*```",
        re.IGNORECASE | re.MULTILINE
    )
    m = pattern.search(md)
    if not m:
        return None
    block = m.group(1).strip()
    for line in block.splitlines():
        line = line.strip()
        if line:
            return line
    return None

# ──────────────────────────────────────────────────────────────────────────────
# Pre-health check
# ──────────────────────────────────────────────────────────────────────────────

def pre_health_check(domain_url: str, cms_provided: str | None = None) -> dict:
    """
    Run a pre-health check on a given domain URL.
    Assumes CMS is provided by the client (no detection/verification).
    """
    results = {
        "domain": domain_url,
        "ssl_valid": domain_url.startswith("https"),
        "response_time_ms": None,
        "mobile_friendly": False,
        "robots_txt_exists": False,
        "sitemap_urls": [],
        "cms_provided": cms_provided
    }

    try:
        # Reachability & latency
        resp = requests.get(domain_url, timeout=10, allow_redirects=True)
        results["response_time_ms"] = int(resp.elapsed.total_seconds() * 1000)

        # robots.txt & sitemaps from robots
        robots_url = urljoin(domain_url, "/robots.txt")
        robots_resp = requests.get(robots_url, timeout=5)
        results["robots_txt_exists"] = robots_resp.status_code == 200

        if results["robots_txt_exists"]:
            for line in robots_resp.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    results["sitemap_urls"].append(line.split(":", 1)[1].strip())

        # fallback to /sitemap.xml
        if not results["sitemap_urls"]:
            sitemap_url = urljoin(domain_url, "/sitemap.xml")
            sitemap_resp = requests.get(sitemap_url, timeout=5)
            if sitemap_resp.status_code == 200:
                results["sitemap_urls"].append(sitemap_url)

        # basic mobile check via viewport meta
        soup = BeautifulSoup(resp.text, "html.parser")
        results["mobile_friendly"] = soup.find("meta", attrs={"name": "viewport"}) is not None

    except Exception as e:
        results["error"] = str(e)

    return results

# ──────────────────────────────────────────────────────────────────────────────
# Persistence
# ──────────────────────────────────────────────────────────────────────────────

def slugify_domain(url: str) -> str:
    """Create a safe filename from a domain URL."""
    s = url.replace("https://", "").replace("http://", "")
    return "".join(ch if ch.isalnum() or ch in "-._" else "_" for ch in s)

def save_results(results: dict, outdir: Path = OUTPUT_DIR) -> Path:
    """Save health check results to JSON under GEO/client docs/health_checks/"""
    outdir.mkdir(parents=True, exist_ok=True)
    domain_slug = slugify_domain(results["domain"])
    path = outdir / f"{domain_slug}_health.json"
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[pre-health] Saved results to: {path}")
    return path

# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not INTAKE_MD.exists():
        raise FileNotFoundError(f"Intake file not found at: {INTAKE_MD}")

    domain = extract_domain_from_md(INTAKE_MD)
    cms = extract_cms_from_md(INTAKE_MD)

    if not domain:
        raise RuntimeError("No domain found in the intake Markdown.")

    print(f"Running pre-health check for: {domain}")
    print(f"Using intake: {INTAKE_MD}")
    results = pre_health_check(domain_url=domain, cms_provided=cms)
    print(results)
    save_results(results)  # -> GEO/client docs/health_checks/<domain>_health.json
